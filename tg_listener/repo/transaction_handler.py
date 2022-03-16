import asyncio
import logging
from asyncio.queues import QueueEmpty, Queue
from threading import Thread

import pandas
from web3 import Web3

from tg_listener.repo.arctic_repo import arctic_db
from util.asyncio.cancelable import Cancelable
from util.uniswap.trade import Trade
from util.web3.transaction import ExtendedTxData

logger = logging.getLogger(__name__)


class SwapHandler(Cancelable):
    def __init__(self, swap_queue: Queue, w3: Web3):
        self.w3 = w3
        self.swap_queue = swap_queue
        self.trade_queue = Queue()

    async def run(self):
        while self.is_running():
            try:
                txs = self.swap_queue.get_nowait()
            except QueueEmpty:
                await asyncio.sleep(0.1)
                continue

            ticks = []
            buys = []
            sells = []
            for tx in txs:
                tx: ExtendedTxData
                trade = Trade.from_transaction(tx.to_tx_data(), tx.receipt, tx.timestamp)
                if not trade:
                    continue

                self.trade_queue.put_nowait(trade)
                # logger.info(trade.to_human())
                if trade.amount_in == 0 or trade.amount_out == 0:
                    logger.warning(str(trade))
                else:
                    price_pair = trade.price_pair
                    arctic_db.add_ticks(price_pair.quote_token, [{
                        'timestamp': trade.timestamp,
                        'price': price_pair.price_in['usd'],
                    }])
                    ticks.append({
                    })
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
