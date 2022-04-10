import dataclasses
import json
from pathlib import Path
from typing import List

import arrow
import pandas
import pytz

from util.big_number.big_number import float_to_str


@dataclasses.dataclass
class TokenResult:
    stat: dict
    ticks: pandas.DataFrame


@dataclasses.dataclass
class TickMakerRule:
    token_results: List[TokenResult] = dataclasses.field(default_factory=list, init=False)

    def gen_key(self):
        raise NotImplemented

    def add(self, stat, data):
        raise NotImplemented

    def save(self, dirpath: Path):
        result = []
        for item in self.token_results:
            stat = dict(item.stat)
            ticks = item.ticks

            ticks['first'] = ticks['first'].apply(float_to_str)
            ticks['last'] = ticks['last'].apply(float_to_str)
            ticks = ticks.tz_localize(pytz.timezone('Asia/Shanghai'))

            stat['ticks'] = json.loads(ticks.to_json(orient='index', date_format='', ))

            result.append(stat)

        save_name = dirpath.joinpath(self.gen_key() + '.json')
        if not save_name.parent.exists():
            save_name.parent.mkdir(parents=True)

        result = {'build_time': arrow.now(), 'items': result}
        with save_name.open('w+') as fp:
            json.dump(result, fp, default=str)
