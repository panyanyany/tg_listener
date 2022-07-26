import dataclasses
from pathlib import Path
from typing import Tuple, Dict, Any, Union

from web3 import Web3
from web3.contract import ContractFunction
from web3.middleware import geth_poa_middleware

from util.eth.abi_force_decoder.signature import new_fn_signature_from_str, FunctionSignature
from util.eth.abi_force_decoder.utils import fn_signature_compose, get_signatures_from_abi
from util.project.project import project_root


class Decoder:
    def __init__(self, lines: [str], w3: Web3 = None):
        w3 = w3 if w3 else Web3()

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
                # (
                #   <Function swapExactTokensForETHSupportingFeeOnTransferTokens(uint256,uint256,address[],address,uint256)>,
                #   {
                #     'amountIn': 174662476028127148025,
                #     'amountOutMin': 25507846803485763,
                #     'deadline': 1646030003,
                #     'path': ['0x4a72AF9609d22Bf2fF227AEC333c7d0860f3dB36', '0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c'],
                #     'to': '0x4FA40e5Dd24eedE393c7DDf53fcDB6Ca887e096C',
                #   },
                # )
                return function_input
            except Exception as e:
                continue


free_mint_signatures = fn_signature_compose(['mint',
                                             'claim',  # 这个可能杀伤力比较大
                                             'free mint', 'mint free', 'mint NFT'],
                                            ['uint16 amt',
                                             'uint amt',
                                             'uint256 amt',
                                             'address to, uint16 amt',
                                             'address to, uint256 amt',
                                             'uint256 _amount, bytes32[] _whitelistProof',
                                             ])
pancake_swap_router_signatures = get_signatures_from_abi(
    Path(__file__).parent.joinpath('./data/abi/pancake_swap_router.json'))


def freemint_decoder(w3: Web3 = None):
    """专门检测 free mint 的 decoder"""
    if w3 is None:
        provider = "https://bsc-dataseed1.binance.org/"  # can also be set through the environment variable `PROVIDER`
        w3 = Web3(Web3.HTTPProvider(provider))
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)  # 注入poa中间件
    return Decoder(free_mint_signatures, w3)
