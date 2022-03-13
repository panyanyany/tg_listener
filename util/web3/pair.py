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


@dataclass
class PricePair(SortedPair):
    price_in: Dict[str, float] = field(default_factory=dict)
    price: float = 0


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
