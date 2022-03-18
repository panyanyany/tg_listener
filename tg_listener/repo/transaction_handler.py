import asyncio
import logging
from asyncio.queues import QueueEmpty, Queue
from threading import Thread

import pandas
from web3 import Web3

from tg_listener.repo.arctic_repo import arctic_db
from util.asyncio.cancelable import Cancelable
from util.bsc.token import has_canonical, all_canonical
from util.uniswap.trade import Trade
from util.web3.transaction import ExtendedTxData

logger = logging.getLogger(__name__)


class SwapHandler(Cancelable):
    def __init__(self, swaps_queue: Queue, w3: Web3):
        self.w3 = w3
        self.swaps_queue = swaps_queue
        self.trades_queue = Queue()

    async def run(self):
        while self.is_running():
            try:
                txs = self.swaps_queue.get_nowait()
            except QueueEmpty:
                await asyncio.sleep(0.1)
                continue

            trades = []
            for tx in txs:
                tx: ExtendedTxData
                trade = Trade.from_extended_tx(tx)
                if not trade:
                    continue

                if not has_canonical([trade.token_in, trade.token_out]):
                    continue
                if all_canonical([trade.token_in, trade.token_out]):
                    continue
                # logger.info(trade.to_human())
                if trade.amount_in == 0 or trade.amount_out == 0:
                    logger.warning(str(trade))
                else:
                    trades.append(trade)
            logger.info(f'swap handler: trades={len(trades)}')
            self.trades_queue.put_nowait(trades)
        logger.info('swap handler stopped')


class LiqHandler(Cancelable):
    def __init__(self, liq_queue: Queue, w3: Web3):
        self.w3 = w3
        self.liq_queue = liq_queue
        self.queue = Queue()

    async def run(self):
        while self.is_running():
            try:
                tx = self.liq_queue.get_nowait()
            except QueueEmpty:
                await asyncio.sleep(0.1)
                continue
        logger.info('liq handler stopped')
