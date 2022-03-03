import asyncio
import logging
from typing import List

from web3 import Web3
from web3.eth import AsyncEth
from web3.middleware import async_geth_poa_middleware
from web3.types import TxReceipt

from util.web3.http_providers import AsyncConcurrencyHTTPProvider

provider = "https://bsc-dataseed1.binance.org/"  # can also be set through the environment variable `PROVIDER`

w3 = Web3(AsyncConcurrencyHTTPProvider(provider), modules={'eth': (AsyncEth,)}, middlewares=[])
w3.middleware_onion.inject(async_geth_poa_middleware, layer=0)  # 注入poa中间件

# txh = '0x39ba3d511176788076f1012538d6354ea4e0b3bb70ec0d0a097002137c442e24'
tx_list = [
    '0xe4aa32946a1019fb8924bd91f3abef4e84c08d71540502217b45cf7912a58179',
    # swapExactTokensForETHSupportingFeeOnTransferTokens
    '0xe4502e017582a3786545d6b6a5b84c1e21a5c4fd1ac22266a4e304a9fa3a1853',  # swapExactTokensForTokens
    '0xb64f4dca8e981b1efd18c4265677dd8838e402a76e78b0f69bdd42557cd963d7',  # swapTokensForExactTokens
    '0x8a47ae500e41ea481289fba363a2bd5cb10295c6a84e61b4fb07e7013ecd0065',  # swapExactETHForTokens
]


async def main():
    gathering = asyncio.gather(*[
        w3.eth.get_transaction_receipt(tx) for tx in tx_list
    ])

    results = await gathering
    failed_cnt = 0
    print(results[0])
    receipts: List[TxReceipt] = []
    for item in results:
        if not item:
            failed_cnt += 1
        else:
            receipts.append(item)
    print(len(results), failed_cnt)


logging.basicConfig(level=logging.DEBUG)
asyncio.run(main())
