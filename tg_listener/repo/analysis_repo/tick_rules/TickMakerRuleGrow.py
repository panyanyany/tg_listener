import dataclasses

from tg_listener.repo.analysis_repo.tick_rules.base import TickMakerRule, TokenResult


@dataclasses.dataclass
class TickMakerRuleGrow(TickMakerRule):
    span: str = ''
    times: float = 0
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
