# main()
import asyncio
from datetime import datetime
from typing import List

from web3 import Web3
from web3.eth import AsyncEth
from web3.middleware import geth_poa_middleware, async_geth_poa_middleware
from web3.types import BlockData, TxData, TxReceipt

from tg_listener.repo.chain_listener import ChainListener
from util.uniswap.trade import Trade
from util.web3.http_providers import AsyncConcurrencyHTTPProvider

block_queue = ChainListener().start()

provider = "https://bsc-dataseed1.binance.org/"  # can also be set through the environment variable `PROVIDER`
w3 = Web3(AsyncConcurrencyHTTPProvider(provider), modules={'eth': (AsyncEth,)}, middlewares=[])
w3.middleware_onion.inject(async_geth_poa_middleware, layer=0)  # 注入poa中间件


async def main():
    while True:
        # 等待新的区块
        block: BlockData = block_queue.get()
        dt = datetime.fromtimestamp(block['timestamp'])

        # 检索出 swap 类型的交易
        swap_cnt = 0
        swap_transactions: [TxData] = []
        for tx in block['transactions']:
            tx: TxData
            fn_details = Trade.router_decoder.decode(tx['input'])
            if not fn_details:
                continue
            fn_name = fn_details[0].fn_name
            if 'swap' in fn_name.lower():
                swap_cnt += 1
                swap_transactions.append(tx)

        print(datetime.now(), block['hash'].hex(), block['number'], dt, len(block['transactions']), swap_cnt)

        # 请求交易结果
        async def get_receipt(tx: TxData):
            try:
                resp = await w3.eth.get_transaction_receipt(tx['hash'])
                return resp
            except:
                return

        await asyncio.sleep(1)
        gathering = asyncio.gather(*[
            get_receipt(tx) for tx in swap_transactions
        ])
        results = await gathering
        failed_cnt = 0
        # print(results[0])
        receipts: List[TxReceipt] = []
        for item in results:
            if not item:
                failed_cnt += 1
            else:
                receipts.append(item)
        print(len(results), failed_cnt)

        # 把结果转换成可读交易类型
        tx_map = {}
        tx_pairs = []
        for tx in swap_transactions:
            tx_map[tx['hash']] = tx

        trades = []
        for receipt in receipts:
            tx = tx_map[receipt['transactionHash']]
            trade = Trade.from_transaction(tx, receipt)
            if not trade:
                continue
            if trade.amount_in == 0 or trade.amount_out == 0:
                print(trade)


asyncio.run(main())
