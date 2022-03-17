import asyncio
import logging
from asyncio.queues import Queue, QueueEmpty
from datetime import datetime
from typing import List

import pandas
from pandas import MultiIndex, Index
from web3 import Web3

from tg_listener.repo.arctic_repo import arctic_db
from util.asyncio.cancelable import Cancelable
from util.uniswap.trade import Trade
from util.web3.transaction import ExtendedTxData

logger = logging.getLogger(__name__)


class DbHandler(Cancelable):
    """分红币处理"""

    def __init__(self, trades_queue: Queue, liq_queue: Queue, w3: Web3):
        self.w3 = w3
        self.trades_queue = trades_queue
        self.liq_queue = liq_queue

    async def run(self):
        token_exists = {}
        while self.is_running():
            trades: List[Trade] = []
            tx: Trade = None
            try:
                trades = self.trades_queue.get_nowait()
            except QueueEmpty:
                pass
            try:
                tx: ExtendedTxData = self.liq_queue.get_nowait()
            except QueueEmpty:
                pass

            if not any([len(trades) > 0, tx]):
                await asyncio.sleep(0.1)
                continue

            if trades:
                await self.handle_trade(trades)
            if tx:
                await self.handle_tx(tx)

    async def handle_trade(self, trades: List[Trade]):
        exists = set()
        for trade in trades:
            d = {'price': trade.price_pair.price_in['usd'], 'hash': trade.hash}
            dt = datetime.fromtimestamp(trade.timestamp)
            key = f'{trade.price_pair.quote_token}:{trade.timestamp}'
            if key in exists:
                continue
            exists.add(key)

            # dt = pandas.datetime(dt.year, dt.month, dt.day)
            df = pandas.DataFrame(d, index=Index([dt], name='date'))
            try:
                arctic_db.add_ticks(trade.price_pair.quote_token, df)
            except BaseException as e:
                logger.error(
                    f'add_ticks failed: hash={trade.hash}'
                    f', token={trade.price_pair.quote_token}'
                    f', date={dt}'
                    f', ts={trade.timestamp}',
                    exc_info=e)

    async def handle_tx(self, tx: ExtendedTxData):
        pass
