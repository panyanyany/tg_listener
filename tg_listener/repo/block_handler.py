import logging
from datetime import datetime

from web3 import Web3
from web3.eth import AsyncEth
from web3.middleware import async_geth_poa_middleware
from web3.types import BlockData

from helper.block_helper import extract_router_transactions, load_receipts
from util.asyncio.cancelable import Cancelable
from util.uniswap.trade import Trade
from util.web3.http_providers import AsyncConcurrencyHTTPProvider


class BlockHandler(Cancelable):
    def __init__(self, block_queue):
        w3 = Web3(AsyncConcurrencyHTTPProvider(), modules={'eth': (AsyncEth,)}, middlewares=[])
        w3.middleware_onion.inject(async_geth_poa_middleware, layer=0)  # 注入poa中间件
        self.w3 = w3
        self.block_queue = block_queue

    async def main(self):
        while self.is_running():
            # 等待新的区块
            block: BlockData = self.block_queue.get()

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
            if self.block_queue.qsize() > 0:
                logging.warning(
                    f"{now}"
                    f", len(txs)={len(block['transactions'])}"
                    f", swap_cnt={len(swap_transactions)}, liq_cnt={len(liq_transactions)}"
                    f", {block['hash'].hex()}, {block['number']}, {dt}"
                    f", delta={(now - dt).total_seconds()}"
                    f", queue={self.block_queue.qsize()}"
                )

            # 把结果转换成可读交易类型
            trades = []
            for tx in swap_transactions:
                trade = Trade.from_transaction(tx.to_tx_data(), tx.receipt)
                if not trade:
                    continue

                if trade.amount_in == 0 or trade.amount_out == 0:
                    print(trade)
