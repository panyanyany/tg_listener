from dataclasses import dataclass
from typing import Union

from dacite import from_dict
from web3 import Web3

from util.bsc import constants


class Multicall:
    def __init__(self, web3: Web3):
        self.web3 = web3
        self.c_multi_call = web3.eth.contract(address=web3.toChecksumAddress(constants.multi_call),
                                              abi=open('./resources/bsc/MultiCall/abi.json').read())

    def get_pair_info_with_price(self, pair_address):
        pair_info = self.c_multi_call.functions.getPairInfoWithPrice(self.web3.toChecksumAddress(pair_address),
                                                                     self.web3.toChecksumAddress(
                                                                         constants.wbnb_busd_pair)).call()
        return PairInfo(*pair_info)

    def get_token_info(self, address):
        token_info = self.c_multi_call.functions.getTokenInfo(self.web3.toChecksumAddress(address)).call()
        return TokenInfo(*token_info)


@dataclass
class TokenInfo:
    addr: str
    name: str
    symbol: str
    decimals: int
    total_supply: int
    balance_of_pair: int
    busd_price: int
    total_busd_amount_of_pair: int
    total_busd_amount_of_pair_human: float = 0
    busd_price_human: float = 0

    def to_human(self):
        self.total_busd_amount_of_pair_human = self.total_busd_amount_of_pair / (10 ** 12)
        self.busd_price_human = self.busd_price / (10 ** 12)
        return self


@dataclass
class PairInfo:
    pair_address: str
    name: str
    symbol: str
    decimals: int
    total_supply: int
    # symbol_1: str
    # symbol_0: str
    token_0: Union[TokenInfo, tuple]
    token_1: Union[TokenInfo, tuple]
    total_busd_amount: int
    farm_tvl: int
    total_busd_amount_human: float = 0

    def to_human(self):
        self.total_busd_amount_human = self.total_busd_amount / (10 ** 18)
        return self

    def __post_init__(self):
        self.token_0 = TokenInfo(*self.token_0)
        self.token_1 = TokenInfo(*self.token_1)
