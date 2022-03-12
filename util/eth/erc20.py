from pathlib import Path

from web3 import Web3


class Erc20:
    def __init__(self, address, web3: Web3):
        self.web3 = web3
        with Path(__file__).parent.joinpath('data/erc20/abi.json').open() as fp:
            abi = fp.read()
        self.c_erc20 = web3.eth.contract(address=web3.toChecksumAddress(address),
                                         abi=abi)

    def decimals(self):
        return self.c_erc20.functions.decimals().call()
