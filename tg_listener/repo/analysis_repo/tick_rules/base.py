import dataclasses
from typing import List

import pandas


@dataclasses.dataclass
class TokenResult:
    stat: dict
    ticks: pandas.DataFrame


@dataclasses.dataclass
class TickMakerRule:
    span: str = ''
    times: float = 0
    token_results: List[TokenResult] = dataclasses.field(default_factory=list)

    def gen_key(self):
        raise NotImplemented

    def add(self, stat, data):
        raise NotImplemented
