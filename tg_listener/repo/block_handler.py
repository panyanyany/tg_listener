import asyncio
import logging
from asyncio import Queue
from asyncio.queues import QueueEmpty
from datetime import datetime

from web3 import Web3
from web3.types import BlockData

from helper.block_helper import extract_router_transactions, load_receipts
from util.asyncio.cancelable import Cancelable

logger = logging.getLogger(__name__)


class BlockHandler(Cancelable):
    def __init__(self, block_queue: Queue, w3: Web3):
        self.w3 = w3
        self.block_queue = block_queue
        self.swap_queue = Queue()
        self.liq_queue = Queue()

    async def run(self):
        await self.loop()
        logger.info('block_handler stopped')

    async def loop(self):
        while self.is_running():
            # 等待新的区块
            try:
                # 在同一线程，不要用 await queue.get(), 会由于生产者队列为空导致一直阻塞，无法退出
                block: BlockData = self.block_queue.get_nowait()
            except QueueEmpty:
                await asyncio.sleep(0.1)
                continue

            # 提取 uniswap 相关交易: swap & liq
            swap_transactions, liq_transactions = extract_router_transactions(block['transactions'])
            # 加载交易结果
            txs = await load_receipts(self.w3, swap_transactions + liq_transactions)
            # 不成功的不要
            txs = filter(lambda e: e.receipt and e.receipt.status == 1, txs)
            # 再次提取 uniswap 相关交易: swap & liq
            swap_transactions, liq_transactions = extract_router_transactions(txs)

            dt = datetime.fromtimestamp(block['timestamp'])
            now = datetime.now()
            if self.block_queue.qsize() >= 0:
                logger.warning(
                    f"{now}"
                    f", len(txs)={len(block['transactions']):03}"
                    f", swap_cnt={len(swap_transactions)}, liq_cnt={len(liq_transactions)}"
                    f", {block['hash'].hex()}, {block['number']}, {dt}"
                    f", delta={(now - dt).total_seconds():.1f}s"
                    f", queue={self.block_queue.qsize()}"
                )

            self.swap_queue.put_nowait(swap_transactions)
            for liq in liq_transactions:
                self.liq_queue.put_nowait(liq)
                # trade = Trade.from_transaction(tx.to_tx_data(), tx.receipt)
                # if not trade:
                #     continue
                #
                # if trade.amount_in == 0 or trade.amount_out == 0:
                #     logger.warning(str(trade))
                # else:
                #     self.tx_queue.put_nowait(trade)
