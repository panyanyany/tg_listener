import dataclasses
import json
from pathlib import Path

import arrow
import pytz

from tg_listener.repo.analysis_repo.tick_rules.base import TickMakerRule, TokenResult
from util.big_number.big_number import float_to_str


@dataclasses.dataclass
class TickMakerRuleGrow(TickMakerRule):
    min_count: int = 1

    def gen_key(self):
        return f"T{self.span}_{self.times}_{self.min_count}"

    def check_min_count(self, data, min_count, times):
        if len(data) < min_count:
            return False
        for i in range(min_count):
            pos = i + 1
            if data.iloc[-pos]['times'] < times:
                return False
        return True

    def add(self, stat, tot_data):
        task = self
        data = tot_data.resample(task.span)['price'].agg(['first', 'last']).dropna()
        data['times'] = (data['last'] - data['first']) / data['first']
        if self.check_min_count(data, task.min_count, task.times):
            self.token_results.append(TokenResult(stat=stat, ticks=data))

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