from web3 import Web3

from util.bsc import constants


class Factory:
    def __init__(self, web3: Web3):
        self.web3 = web3
        self.c_factory = web3.eth.contract(address=web3.toChecksumAddress(constants.factory),
                                           abi=open('./resources/bsc/PancakeFactory/abi.json').read())

    def get_pair(self, base_addr, quote_addr):
        pair_info = self.c_factory.functions.getPair(
            self.web3.toChecksumAddress(base_addr),
            self.web3.toChecksumAddress(quote_addr),
        ).call()
        return pair_info
