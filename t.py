import dataclasses
import json

from web3 import Web3
from web3.middleware import geth_poa_middleware
from beeprint import pp

from util.bsc import constants
from util.eth.abi_force_decoder.decoder import freemint_decoder, Decoder, pancake_swap_router_signatures

provider = "https://bsc-dataseed1.binance.org/"  # can also be set through the environment variable `PROVIDER`

w3 = Web3(Web3.HTTPProvider(provider))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)  # 注入poa中间件

router_decoder = Decoder(w3, pancake_swap_router_signatures)

contract = w3.eth.contract(w3.toChecksumAddress(constants.busd), abi=open('./storage/erc20_abi.json').read())
abi_events = [abi for abi in contract.abi if abi["type"] == "event"]

# txh = '0x39ba3d511176788076f1012538d6354ea4e0b3bb70ec0d0a097002137c442e24'
txh = '0xe4aa32946a1019fb8924bd91f3abef4e84c08d71540502217b45cf7912a58179'


def dec_log(log):
    """https://medium.com/coinmonks/unlocking-the-secrets-of-an-ethereum-transaction-3a33991f696c"""
    receipt_event_signature_hex = w3.toHex(log.topics[0])
    for event in abi_events:
        # Get event signature components
        name = event["name"]
        inputs = [param["type"] for param in event["inputs"]]
        inputs = ",".join(inputs)
        # Hash event signature
        event_signature_text = f"{name}({inputs})"
        # print(event_signature_text)
        event_signature_hex = w3.toHex(w3.keccak(text=event_signature_text))
        # Find match between log's event signature and ABI's event signature
        if event_signature_hex == receipt_event_signature_hex:
            # Decode matching log
            # decoded_logs = contract.events[event["name"]]().processReceipt(receipt)
            # print(decoded_logs)
            decoded_log = contract.events[event["name"]]().processLog(log)
            # {
            #   'address': '0x4a72AF9609d22Bf2fF227AEC333c7d0860f3dB36',
            #   'args': AttributeDict({'from': '0x4FA40e5Dd24eedE393c7DDf53fcDB6Ca887e096C', 'to': '0x0000000000000000000000000000000000000000', 'value': 2619937140421907220})
            #   'blockHash': HexBytes('0x1c5c6476c66b8675879459bf908b1e17bf2aac8154b52139f34e76372c6cf2be')
            #   'blockNumber': 15643090,
            #   'event': 'Transfer',
            #   'logIndex': 473,
            #   'transactionHash': HexBytes('0xe4aa32946a1019fb8924bd91f3abef4e84c08d71540502217b45cf7912a58179')
            #   'transactionIndex': 135,
            # }
            return decoded_log


tx = w3.eth.get_transaction(txh)
fn = router_decoder.decode(tx.input)
pp(fn)

rec = w3.eth.get_transaction_receipt(txh)
logs = []
for log in rec.logs:
    logs.append(dict(log))
    smart_contract = log["address"]
    dlog = dec_log(log)
    if not dlog:
        continue
    if dlog['event'] != 'Transfer':
        continue
    print(f"Contract:{dlog['address']}, {dlog['event']}({dict(dlog['args'])})")

    # print(dict(log))

# pp(dict(rec))
