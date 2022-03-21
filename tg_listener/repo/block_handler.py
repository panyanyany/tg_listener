import asyncio
import logging
from asyncio import Queue
from asyncio.queues import QueueEmpty
from datetime import datetime
from typing import List

from web3 import Web3
from web3.types import BlockData

from helper.block_helper import extract_router_transactions, load_receipts
from util.asyncio.cancelable import Cancelable, CancelableTiktok
from util.bsc.constants import busd, usdt, usdc, wbnb, cake
from util.web3.transaction import ExtendedTxData

logger = logging.getLogger(__name__)


class BlockHandler(CancelableTiktok):
    def __init__(self, block_queue: Queue, w3: Web3):
        self.w3 = w3
        self.block_queue = block_queue
        self.swaps_queue = Queue()
        self.liq_queue = Queue()
        self.blocks = []

    def all_in_canonical(self, paths: List[str]):
        for token in paths:
            if token.lower() not in [busd, usdt, usdc, wbnb, cake]:
                return False
        return True

    async def _run(self):
        await self.tiktok(1, self.get_block, self.process_blocks)

    async def get_block(self):
        # 等待新的区块
        try:
            # 在同一线程，不要用 await queue.get(), 会由于生产者队列为空导致一直阻塞，无法退出
            block: BlockData = self.block_queue.get_nowait()
            self.blocks.append(block)
        except QueueEmpty:
            pass

    async def process_blocks(self):
        # logger.info(f"got block: id={block['number']}")
        if len(self.blocks) == 0:
            return
        txs = []

        block_dt = []
        for block in self.blocks:
            dt = datetime.fromtimestamp(block['timestamp'])
            block_dt.append(dt)
            ts_diff = (datetime.now() - dt).total_seconds()
            logger.debug(f"txs_cnt={len(block['transactions'])}, hash={block['hash'].hex()}, number={block['number']}"
                         f", ts_diff={ts_diff:.1f}")
            for tx in block['transactions']:
                tx2 = ExtendedTxData.from_tx_data(block, tx)
                txs.append(tx2)

        # 提取 uniswap 相关交易: swap & liq
        swap_transactions, liq_transactions = extract_router_transactions(txs)
        # 如果是权威货币之间互相交易，也不要
        swap_transactions = list(
            filter(lambda e: not self.all_in_canonical(e.fn_details[1]['path']), swap_transactions))
        # 加载交易结果
        await load_receipts(self.w3, swap_transactions + liq_transactions)
        # 不成功的不要
        swap_transactions = list(filter(lambda e: e.receipt and e.receipt.status == 1, swap_transactions))
        liq_transactions = list(filter(lambda e: e.receipt and e.receipt.status == 1, liq_transactions))

        now = datetime.now()
        block_dt.sort()
        logger.info(
            f"block_cnt={len(self.blocks)}, txs_cnt={len(txs):03}"
            f", swap_cnt={len(swap_transactions)}, liq_cnt={len(liq_transactions)}"
            f", queue={self.block_queue.qsize()}"
            f", ts_diff=({(now - block_dt[0]).total_seconds():.0f},{(now - block_dt[-1]).total_seconds():.0f})"
        )

        self.swaps_queue.put_nowait(swap_transactions)
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
        self.blocks.clear()
