import json

from hexbytes import HexBytes
from web3 import Web3
from web3.types import TxData
from web3.datastructures import AttributeDict
from web3.middleware import geth_poa_middleware
from beeprint import pp
from web3.types import TxReceipt

from util.eth.abi_force_decoder.decoder import Decoder, pancake_swap_router_signatures
from util.eth.erc20.log_decoder import LogDecoder
from util.uniswap.trade import Trade

provider = "https://bsc-dataseed1.binance.org/"  # can also be set through the environment variable `PROVIDER`

w3 = Web3(Web3.HTTPProvider(provider))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)  # 注入poa中间件

router_decoder = Decoder(pancake_swap_router_signatures, w3)

# txh = '0x39ba3d511176788076f1012538d6354ea4e0b3bb70ec0d0a097002137c442e24'
tx_list = [
    '0xe4aa32946a1019fb8924bd91f3abef4e84c08d71540502217b45cf7912a58179',
    # swapExactTokensForETHSupportingFeeOnTransferTokens
    '0xe4502e017582a3786545d6b6a5b84c1e21a5c4fd1ac22266a4e304a9fa3a1853',  # swapExactTokensForTokens
    '0xb64f4dca8e981b1efd18c4265677dd8838e402a76e78b0f69bdd42557cd963d7',  # swapTokensForExactTokens
    '0x8a47ae500e41ea481289fba363a2bd5cb10295c6a84e61b4fb07e7013ecd0065',  # swapExactETHForTokens
]


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, HexBytes):
            return obj.hex()
        if isinstance(obj, AttributeDict):
            return dict(obj)
        return json.dumps(obj)


for txh in tx_list:
    tx = w3.eth.get_transaction(txh)
    rec = w3.eth.get_transaction_receipt(txh)
    print(Trade.from_transaction(tx, rec))
