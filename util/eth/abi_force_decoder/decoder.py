import dataclasses
from typing import Tuple, Dict, Any, Union

from web3 import Web3
from web3.contract import ContractFunction
from web3.middleware import geth_poa_middleware

from util.eth.abi_force_decoder.signature import new_fn_signature_from_str, FunctionSignature
from util.eth.abi_force_decoder.utils import fn_signature_compose


class Decoder:
    def __init__(self, w3: Web3, lines: [str]):
        self.w3 = w3
        self.fn_signatures: [FunctionSignature] = []
        self.test_contracts = []
        for line in lines:
            fn_sig = new_fn_signature_from_str(line)
            self.fn_signatures.append(fn_sig)

            abi = [dataclasses.asdict(fn_sig)]
            # print(abi)
            c = w3.eth.contract(address=w3.toChecksumAddress('0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c'), abi=abi)
            self.test_contracts.append(c)

    def decode(self, data: str) -> Union[None, Tuple['ContractFunction', Dict[str, Any]]]:
        for c in self.test_contracts:
            try:
                function_input = c.decode_function_input(data)
                return function_input
            except Exception as e:
                continue


lines = fn_signature_compose(['mint',
                              'claim',  # 这个可能杀伤力比较大
                              'free mint', 'mint free', 'mint NFT'],
                             ['uint16 amt',
                              'uint amt',
                              'uint256 amt',
                              'address to, uint16 amt',
                              'address to, uint256 amt',
                              'uint256 _amount, bytes32[] _whitelistProof',
                              ])


def freemint_decoder(w3: Web3 = None):
    if w3 is None:
        provider = "https://bsc-dataseed1.binance.org/"  # can also be set through the environment variable `PROVIDER`
        w3 = Web3(Web3.HTTPProvider(provider))
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)  # 注入poa中间件
    return Decoder(w3, lines)
