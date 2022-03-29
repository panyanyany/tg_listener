from web3 import Web3, HTTPProvider
from web3.eth import AsyncEth
from web3.middleware import async_geth_poa_middleware

import settings
from util.web3.http_providers import AsyncConcurrencyHTTPProvider

async_bsc_web3 = Web3(AsyncConcurrencyHTTPProvider(endpoints=settings.endpoints), modules={'eth': (AsyncEth,)},
                      middlewares=[])
async_bsc_web3.middleware_onion.inject(async_geth_poa_middleware, layer=0)  # 注入poa中间件

bsc_web3 = Web3(HTTPProvider('https://bsc-dataseed1.binance.org/'))
