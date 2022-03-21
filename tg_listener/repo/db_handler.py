import asyncio
import logging
from asyncio.queues import Queue, QueueEmpty
from datetime import datetime
from typing import List

import pandas
from pandas import MultiIndex, Index
from web3 import Web3

from tg_listener.repo.arctic_repo import arctic_db
from tg_listener.services import token_service, price_service, lp_service
from tg_listener.services.base_service import ServiceStopped
from util.asyncio.cancelable import Cancelable
from util.bsc.constants import wbnb, cake, usdt, busd, usdc
from util.uniswap.liquidity import LiquidityChange
from util.uniswap.trade import Trade
from util.bsc.token import get_token_name, canonicals, StdToken, has_canonical
from util.web3.pair import sort_pair, PricePair
from util.web3.transaction import ExtendedTxData

logger = logging.getLogger(__name__)


class DbHandler(Cancelable):
    """分红币处理"""

    def __init__(self, trades_queue: Queue, liq_queue: Queue, w3: Web3):
        self.w3 = w3
        self.trades_queue = trades_queue
        self.liq_queue = liq_queue
        self.last_db_insert = 0

    async def run(self):
        token_exists = {}
        while self.is_running():
            trades: List[Trade] = []
            liq: ExtendedTxData = None
            try:
                trades = self.trades_queue.get_nowait()
            except QueueEmpty:
                pass
            try:
                liq: ExtendedTxData = self.liq_queue.get_nowait()
            except QueueEmpty:
                pass

            if not any([len(trades) > 0, liq]):
                await asyncio.sleep(0.1)
                continue

            if trades:
                logger.info(f'trades={len(trades)}')
                await self.handle_trade(trades)
            if liq:
                await self.handle_liq(liq)

    async def handle_trade(self, trades: List[Trade]):
        exists = set()
        added = 0
        for trade in trades:
            dt = datetime.fromtimestamp(trade.timestamp)
            key = f'{trade.price_pair.quote_token}:{trade.timestamp}'
            if key in exists:
                continue
            exists.add(key)

            # 判断交易方向：BUY / SELL
            name = get_token_name(trade.price_pair.base_token)
            direction = 'BUY' if has_canonical([trade.token_in]) else 'SELL'
            if has_canonical([trade.token_in]):
                value = trade.amount_in
                value_token = trade.token_in
            elif has_canonical([trade.token_out]):
                value = trade.amount_out
                value_token = trade.token_out
            else:
                value = 0
                value_token = ''

            decimals = await token_service.inst.get(value_token)
            if value_token == wbnb:
                value = (value / (10 ** decimals)) * await price_service.inst.get_bnb_price()
            elif value_token == cake:
                decimals = await token_service.inst.get(value_token)
                value = (value / (10 ** decimals)) * await price_service.inst.get_cake_price()
            elif value_token in [usdt, usdc, busd]:
                value = (value / (10 ** decimals))

            pools = {name: trade.price_pair.base_res / (10 ** trade.price_pair.base_decimals)}
            d = {'price': trade.price_pair.price_in['usd'],
                 'hash': trade.hash,
                 'direction': direction,
                 'value': value,
                 'operator': trade.operator,
                 **pools}
            # logger.debug('trade: %s, d: %s', trade, d)
            df = pandas.DataFrame(d, index=Index([dt], name='date'))
            try:
                arctic_db.add_ticks(trade.price_pair.quote_token, df)
                # 更新池子
                arctic_db.update_stat(trade.price_pair.quote_token,
                                      pools=pools, is_dividend=trade.is_dividend)
                added += 1
            except BaseException as e:
                logger.error(
                    f'add_ticks failed: hash={trade.hash}'
                    f', token={trade.price_pair.quote_token}'
                    f', date={dt}'
                    f', ts={trade.timestamp}',
                    exc_info=e)

        speed = 0
        if self.last_db_insert:
            diff = (datetime.now() - self.last_db_insert).total_seconds()
            if diff > 0:
                speed = added / diff
            self.last_db_insert = datetime.now()
        logger.info(f'db ticks inserted: {added}, speed={speed:.1f}')

    async def handle_liq(self, liq_tx: ExtendedTxData):
        # logger.info(f'liq changed: {liq.hash.hex()} %s', liq.fn_details)
        liq = LiquidityChange.from_transaction(liq_tx.to_tx_data(), liq_tx.receipt, timestamp=liq_tx.timestamp)
        if not liq:
            return
        try:
            decimals0 = await token_service.inst.get(liq.token0)
            decimals1 = await token_service.inst.get(liq.token1)
        except ServiceStopped:
            return
        pair = sort_pair(liq.token0, liq.token1, liq.amount0, liq.amount1, decimals0, decimals1)
        if not pair:
            return

        price_pair = PricePair.from_sorted_pair(pair)
        try:
            price_pair.bnb_price = await price_service.inst.get_bnb_price()
            price_pair.cake_price = await price_service.inst.get_cake_price()
        except ServiceStopped:
            return
        price_pair.calc()

        # logger.info('liq changed: %s, price_pair=%s', liq, price_pair)
        dt = datetime.fromtimestamp(liq.timestamp)

        amount_in = dict(zip(StdToken.values(), [0, 0, 0, 0, 0]))
        amount_in[get_token_name(price_pair.base_token)] = price_pair.base_res / (10 ** price_pair.base_decimals)

        # logger.info('amount_in: %s', amount_in)
        d = {'hash': liq.hash,
             'value': price_pair.price_in['usd'],
             'operator': liq.operator,
             'method': liq.method_type,
             **amount_in}
        # logger.debug('liq changed: liq=%s, price_pair=%s, d=%s', liq, price_pair, d)
        df = pandas.DataFrame(d, index=Index([dt], name='date'))
        arctic_db.add_liq(price_pair.quote_token, liq.method_type, df, amount_in)
