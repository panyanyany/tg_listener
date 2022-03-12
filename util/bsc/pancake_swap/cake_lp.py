from pathlib import Path

from web3 import Web3


class CakeLp:
    def __init__(self, address, web3: Web3):
        self.web3 = web3
        with Path(__file__).parent.joinpath('../data/CakeLp/abi.json').open() as fp:
            abi = fp.read()
        self.c_cake_lp = web3.eth.contract(address=web3.toChecksumAddress(address),
                                           abi=abi)

    def token0(self):
        return self.c_cake_lp.functions.token0().call()

    def token1(self):
        return self.c_cake_lp.functions.token1().call()
