from web3 import Web3
from web3.middleware import geth_poa_middleware
from beeprint import pp

provider = "https://bsc-dataseed1.binance.org/"  # can also be set through the environment variable `PROVIDER`
w3 = Web3(Web3.HTTPProvider(provider))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)  # 注入poa中间件

block = w3.eth.get_block('latest', True)
for tx in block.transactions:
    print(tx)
    print()
