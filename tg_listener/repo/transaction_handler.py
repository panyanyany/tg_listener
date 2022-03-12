import asyncio
import logging
import queue
from asyncio.queues import QueueEmpty
from threading import Thread

from web3 import Web3

from util.asyncio.cancelable import Cancelable
from util.uniswap.trade import Trade

logger = logging.getLogger(__name__)


class SwapHandler(Cancelable):
    def __init__(self, swap_queue: queue.Queue, w3: Web3):
        self.w3 = w3
        self.swap_queue = swap_queue
        self.queue = queue.Queue()

    async def run(self):
        while self.is_running():
            try:
                txs = self.swap_queue.get_nowait()
            except QueueEmpty:
                await asyncio.sleep(0.1)
                continue

            for tx in txs:
                trade = Trade.from_transaction(tx.to_tx_data(), tx.receipt)
                if not trade:
                    continue

                if trade.amount_in == 0 or trade.amount_out == 0:
                    logger.warning(str(trade))
        logger.info('swap handler stopped')


class LiqHandler(Cancelable):
    def __init__(self, liq_queue: queue.Queue, w3: Web3):
        self.w3 = w3
        self.liq_queue = liq_queue
        self.queue = queue.Queue()

    async def run(self):
        while self.is_running():
            try:
                tx = self.liq_queue.get_nowait()
            except QueueEmpty:
                await asyncio.sleep(0.1)
                continue
        logger.info('liq handler stopped')
