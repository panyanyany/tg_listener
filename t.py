import dataclasses

from web3 import Web3
from web3.middleware import geth_poa_middleware

from util.eth.abi_force_decoder.decoder import Decoder, DefaultDecoder
from util.eth.abi_force_decoder.signature import new_fn_signature_from_str
from util.eth.abi_force_decoder.utils import fn_signature_compose

provider = "https://bsc-dataseed1.binance.org/"  # can also be set through the environment variable `PROVIDER`

w3 = Web3(Web3.HTTPProvider(provider))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)  # 注入poa中间件

h = '0xad6ac81b000000000000000000000000000000000000000000000000000000000000000a'

decoder = DefaultDecoder()
print(decoder.decode(h))
