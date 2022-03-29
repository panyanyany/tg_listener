import dataclasses
from dataclasses import dataclass, Field, field
from typing import Optional, Dict

from util.bsc.constants import busd, usdt, wbnb, cake, usdc


@dataclass
class SortedPair:
    quote_token: str
    quote_res: int

    base_token: str
    base_res: int

    quote_decimals: int = None
    base_decimals: int = None
    lp: str = None


@dataclass
class PricePair(SortedPair):
    price_in: Dict[str, float] = field(default_factory=dict)
    price: float = 0

    bnb_price: float = 0
    cake_price: float = 0

    value: float = 0

    @classmethod
    def from_sorted_pair(cls, pair):
        return PricePair(**dataclasses.asdict(pair))

    def calc(self):
        pair = self
        if pair.quote_decimals > 0:
            quote_res_human = pair.quote_res / (10 ** pair.quote_decimals)
        else:
            quote_res_human = pair.quote_res
        if pair.base_decimals > 0:
            base_res_human = pair.base_res / (10 ** pair.base_decimals)
        else:
            base_res_human = pair.base_res

        if quote_res_human > 0:
            pair.price = base_res_human / quote_res_human
        else:
            pair.price = 0
        if pair.base_token in [busd, usdt, usdc]:
            pair.price_in['usd'] = pair.price
            pair.value = base_res_human
        elif pair.base_token in [wbnb]:
            pair.price_in['bnb'] = pair.price
            pair.value = base_res_human * self.bnb_price
        elif pair.base_token in [cake]:
            pair.price_in['cake'] = pair.price
            pair.value = base_res_human * self.cake_price

        if 'usd' not in pair.price_in:
            if 'bnb' in pair.price_in and self.bnb_price:
                pair.price_in['usd'] = pair.price_in['bnb'] * self.bnb_price
            elif 'cake' in pair.price_in and self.cake_price:
                pair.price_in['usd'] = pair.price_in['cake'] * self.cake_price
        return self


def sort_pair(token0, token1, res0, res1, decimals0=None, decimals1=None) -> Optional[SortedPair]:
    price_ok = True

    for std in [busd, usdt, usdc, wbnb, cake]:
        price_ok = True
        if token0 == std:
            base_token = token0
            base_res = res0
            base_decimals = decimals0

            quote_token = token1
            quote_res = res1
            quote_decimals = decimals1
        elif token1 == std:
            base_token = token1
            base_res = res1
            base_decimals = decimals1

            quote_token = token0
            quote_res = res0
            quote_decimals = decimals0
        else:
            price_ok = False

        if price_ok:
            break

    if not price_ok:
        return None
    return SortedPair(quote_token=quote_token, quote_res=quote_res, base_token=base_token, base_res=base_res,
                      quote_decimals=quote_decimals, base_decimals=base_decimals)
