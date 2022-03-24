import logging
from asyncio.queues import Queue, QueueEmpty
from datetime import datetime
from typing import List

import objgraph
import pandas
from pandas import Index
from web3 import Web3

from tg_listener.repo.arctic_repo.arctic_repo import arctic_db
from tg_listener.services import token_service, price_service
from tg_listener.services.base_service import ServiceStopped
from util.asyncio.cancelable import CancelableTiktok
from util.bsc.constants import wbnb, cake, usdt, busd, usdc
from util.uniswap.liquidity import LiquidityChange
from util.uniswap.trade import Trade
from util.bsc.token import get_token_name, canonicals, StdToken, has_canonical
from util.web3.pair import sort_pair, PricePair
from util.web3.transaction import ExtendedTxData

logger = logging.getLogger(__name__)


class DbHandler(CancelableTiktok):
    """把交易写入数据库"""

    def __init__(self, trades_queue: Queue, liq_queue: Queue, w3: Web3):
        self.w3 = w3
        self.trades_queue = trades_queue
        self.liq_queue = liq_queue
        self.last_db_insert = 0
        self.init_insert_time = 0
        self.total_insert_cnt = 0
        self.trades = []
        self.liqs = []
        self.added = 0

    async def _run(self):
        await self.tiktok(30, self.get_items, self.process)

    async def get_items(self):
        try:
            self.trades += self.trades_queue.get_nowait()
        except QueueEmpty:
            pass
        try:
            self.liqs += [self.liq_queue.get_nowait()]
        except QueueEmpty:
            pass

    async def process(self):
        if self.trades:
            logger.info(f'trades={len(self.trades)}')
            await self.handle_trades(self.trades)
            self.trades = []
        if self.liqs:
            for liq in self.liqs:
                await self.handle_liq(liq)
            self.liqs = []

    async def handle_trades(self, trades: List[Trade]):
        c_time_start = datetime.now()
        tot_df, token_cnt, tot_stat = await self.merge_trades(trades)

        for token in tot_df:
            df = tot_df[token]
            arctic_db.add_ticks(token, df)
            # 更新池子
            stat = arctic_db.get_stat(token)
            pools = stat['pools'] or {}
            pools.update(tot_stat[token]['pools'])
            tot_value = 0
            for c_token in canonicals:
                c_name = get_token_name(c_token)
                if c_name not in pools:
                    continue
                if c_token in [wbnb]:
                    tot_value += pools[c_name] * await price_service.inst.get_bnb_price()
                elif c_token in [cake]:
                    tot_value += pools[c_name] * await price_service.inst.get_cake_price()
                else:
                    tot_value += pools[c_name]

            pools['TOTAL'] = tot_value
            arctic_db.update_stat(token,
                                  pools=pools, is_dividend=tot_stat[token]['is_dividend'])

        self.total_insert_cnt += self.added
        speed = 0
        avg_speed = 0
        if self.last_db_insert:
            diff = (datetime.now() - self.last_db_insert).total_seconds()
            if diff > 0:
                speed = self.added / diff

        if self.init_insert_time:
            avg_diff = (datetime.now() - self.init_insert_time).total_seconds()
            if avg_diff > 0:
                avg_speed = self.total_insert_cnt / avg_diff

        c_time_diff = (datetime.now() - c_time_start).total_seconds()
        insert_db_speed = 0
        if c_time_diff > 0:
            insert_db_speed = self.added / c_time_diff
        logger.info(
            f'db stat: {self.added}/{len(token_cnt)}, speed={speed:.1f}, avg_speed={avg_speed:.1f}'
            f', c_time={c_time_diff:.1f}, insert_db_speed={insert_db_speed:.1f}')
        objgraph.show_most_common_types(limit=10)
        if not self.last_db_insert:
            self.init_insert_time = datetime.now()
        self.last_db_insert = datetime.now()

    async def merge_trades(self, trades: List[Trade]):
        exists = set()
        added = 0
        token_cnt = {}
        tot_df = {}
        tot_stat = {}
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

            quote_token = trade.price_pair.quote_token

            pools = {name: trade.price_pair.base_res / (10 ** trade.price_pair.base_decimals)}
            tot_stat.setdefault(quote_token, {})
            tot_stat[quote_token].setdefault('pools', {})
            tot_stat[quote_token]['pools'].update(pools)
            tot_stat[quote_token]['is_dividend'] = trade.is_dividend

            d = {'price': trade.price_pair.price_in['usd'],
                 'hash': trade.hash,
                 'direction': direction,
                 'value': value,
                 'operator': trade.operator,
                 **pools}
            # logger.debug('trade: %s, d: %s', trade, d)
            df = pandas.DataFrame(d, index=Index([dt], name='date'))
            if quote_token not in tot_df:
                tot_df[quote_token] = df
            else:
                tot_df[quote_token] = pandas.concat([tot_df[quote_token], df])
            token_cnt.setdefault(trade.price_pair.quote_token, 0)
            token_cnt[trade.price_pair.quote_token] += 1
            added += 1
        self.added = added
        return tot_df, token_cnt, tot_stat

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
