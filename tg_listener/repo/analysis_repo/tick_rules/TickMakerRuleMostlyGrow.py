import dataclasses
from datetime import datetime

import pandas as pd

from tg_listener.repo.analysis_repo.tick_rules.base import TickMakerRule, TokenResult


@dataclasses.dataclass
class TickMakerRuleMostlyGrow(TickMakerRule):
    span: str = ''
    times: float = 0
    child_span: str = ''
    child_error: float = 0

    def add(self, stat, tot_data: pd.DataFrame):
        now = datetime.now()
        oldest = now - pd.to_timedelta(self.span)
        data: pd.DataFrame = tot_data.loc[oldest:]

        data = data.resample(self.child_span)['price'].agg(['first', 'last']).dropna()

        child_span_count = int(pd.to_timedelta(self.span) / pd.to_timedelta(self.child_span))
        if len(data) < child_span_count:
            print(stat['token'], f'{len(data)} < child_span_count')
            return False

        if (data.iloc[-1]['last'] - data.iloc[0]['first']) / data.iloc[0]['first'] < self.times:
            print(stat['token'], '< self.times')
            return False

        data['times'] = (data['last'] - data['first']) / data['first']
        if len(data[data['times'] < -self.child_error]) > 0:
            print(stat['token'], '低于 child_error')
            return False

        self.token_results.append(TokenResult(stat=stat, ticks=data))

    def gen_key(self):
        return f"TM{self.span}_{self.times}_{self.child_span}"
