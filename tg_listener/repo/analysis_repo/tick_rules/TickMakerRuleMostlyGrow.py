import dataclasses

from tg_listener.repo.analysis_repo.tick_rules.base import TickMakerRule


@dataclasses.dataclass
class TickMakerRuleMostlyGrow(TickMakerRule):
    child_span: str = ''

    def gen_key(self):
        return f"TM{self.span}_{self.times}_{self.child_span}"