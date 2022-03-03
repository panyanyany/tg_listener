from pathlib import Path
from typing import Union

from web3 import Web3
from web3.types import LogReceipt, EventData

from util.bsc import constants


class LogDecoder:
    def __init__(self, w3: Web3 = None):
        w3 = w3 if w3 else Web3()

        self.w3 = w3
        self.contract = self.w3.eth.contract(self.w3.toChecksumAddress(constants.busd),
                                             abi=open(
                                                 Path(__file__).parent.joinpath('./data/erc20_event_abi.json')).read())
        self.abi_events = [abi for abi in self.contract.abi if abi["type"] == "event"]

    def decode(self, log: LogReceipt) -> Union[EventData, None]:
        """把日志解码为转账事件
        https://medium.com/coinmonks/unlocking-the-secrets-of-an-ethereum-transaction-3a33991f696c
        """
        receipt_event_signature_hex = self.w3.toHex(log['topics'][0])
        for event in self.abi_events:
            # Get event signature components
            name = event["name"]
            inputs = [param["type"] for param in event["inputs"]]
            inputs = ",".join(inputs)
            # Hash event signature
            event_signature_text = f"{name}({inputs})"
            # print(event_signature_text)
            event_signature_hex = self.w3.toHex(self.w3.keccak(text=event_signature_text))
            # Find match between log's event signature and ABI's event signature
            if event_signature_hex == receipt_event_signature_hex:
                # Decode matching log
                # decoded_logs = contract.events[event["name"]]().processReceipt(receipt)
                # print(decoded_logs)
                decoded_log = self.contract.events[event["name"]]().processLog(log)
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
                if decoded_log['event'] != 'Transfer':
                    return
                return decoded_log
