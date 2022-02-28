from web3 import Web3
from web3.middleware import geth_poa_middleware
from beeprint import pp
from web3.types import TxReceipt

from util.eth.abi_force_decoder.decoder import Decoder, pancake_swap_router_signatures
from util.eth.erc20.log_decoder import LogDecoder

provider = "https://bsc-dataseed1.binance.org/"  # can also be set through the environment variable `PROVIDER`

w3 = Web3(Web3.HTTPProvider(provider))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)  # 注入poa中间件

router_decoder = Decoder(w3, pancake_swap_router_signatures)

# txh = '0x39ba3d511176788076f1012538d6354ea4e0b3bb70ec0d0a097002137c442e24'
txh = '0xe4aa32946a1019fb8924bd91f3abef4e84c08d71540502217b45cf7912a58179'

tx = w3.eth.get_transaction(txh)
fn = router_decoder.decode(tx.input)
pp(fn)

log_decoder = LogDecoder(w3)

rec: TxReceipt = w3.eth.get_transaction_receipt(txh)
logs = []
for log in rec.logs:
    logs.append(dict(log))
    smart_contract = log["address"]
    dlog = log_decoder.decode(log)
    if not dlog:
        continue
    print(f"Contract:{dlog['address']}, {dlog['event']}({dict(dlog['args'])})")

    # print(dict(log))

# pp(dict(rec))
