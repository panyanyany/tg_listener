import dataclasses
import logging
from datetime import datetime

import pandas as pd

from tg_listener.repo.analysis_repo.tick_rules.base import TickMakerRule, TokenResult

logger = logging.getLogger(__name__)


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
            logger.info(f"{stat['name']} {stat['token']} {len(data)} < child_span_count")
            return False

        tot_times = (data.iloc[-1]['last'] - data.iloc[0]['first']) / data.iloc[0]['first']
        if tot_times < self.times:
            logger.info(f"{stat['name']} {stat['token']} {tot_times} < self.times")
            return False

        data['times'] = (data['last'] - data['first']) / data['first']
        low_errors = data[data['times'] < -self.child_error]
        if len(low_errors) > 0:
            logger.info(f"{stat['name']} {stat['token']} {len(low_errors)} > 0")
            return False

        self.token_results.append(TokenResult(stat=stat, ticks=data))

    def gen_key(self):
        return f"TM{self.span}_{self.times}_{self.child_span}"
