# main()
import asyncio
from datetime import datetime

from web3 import Web3
from web3.eth import AsyncEth
from web3.middleware import geth_poa_middleware, async_geth_poa_middleware
from web3.types import BlockData, TxData

from tg_listener.repo.chain_listener import ChainListener
from util.uniswap.trade import Trade

block_queue = ChainListener().start()

provider = "https://bsc-dataseed1.binance.org/"  # can also be set through the environment variable `PROVIDER`
w3 = Web3(Web3.AsyncHTTPProvider(provider), modules={'eth': (AsyncEth,)}, middlewares=[])
w3.middleware_onion.inject(async_geth_poa_middleware, layer=0)  # 注入poa中间件


async def main():
    while True:
        block: BlockData = block_queue.get()
        dt = datetime.fromtimestamp(block['timestamp'])

        swap_cnt = 0
        txs = []
        for tx in block['transactions']:
            tx: TxData
            fn_details = Trade.router_decoder.decode(tx['input'])
            if not fn_details:
                continue
            fn_name = fn_details[0].fn_name
            if 'swap' in fn_name.lower():
                swap_cnt += 1
                txs.append(tx)

        print(datetime.now(), block['hash'].hex(), block['number'], dt, len(block['transactions']), swap_cnt)

        async def get_receipt(tx: TxData):
            try:
                resp = await w3.eth.get_transaction_receipt(tx['hash'])
                return resp
            except:
                return

        gathering = asyncio.gather(*[
            get_receipt(tx) for tx in txs
        ])
        results = await gathering
        failed_cnt = 0
        print(results[0])
        for item in results:
            if not item:
                failed_cnt += 1
        print(len(results), failed_cnt)


asyncio.run(main())
