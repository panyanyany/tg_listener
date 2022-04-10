import logging
from pathlib import Path

import pandas as pd

from tg_listener.repo.analysis_repo import tick_maker
from tg_listener.repo.analysis_repo.tick_rules.TickMakerRuleGrow import TickMakerRuleGrow
from tg_listener.repo.analysis_repo.tick_rules.TickMakerRuleMostlyGrow import TickMakerRuleMostlyGrow
from util.log_util import setup3, default_ignore_names

setup3(ignore_names=list(set(['web3.*', 'asyncio'] + default_ignore_names) - {'util.*'}))

logger = logging.getLogger(__name__)

pd.set_option('display.width', 1000)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', None)
# pd.set_option('display.max_rows', None)

logger.info('start')

maker = tick_maker.TickMaker([
    TickMakerRuleGrow(span='15min', times=0.1),
    TickMakerRuleGrow(span='1h', times=0.1),
    # TickMakerRuleGrow(span='1h', times=0.01, min_count=3),
    TickMakerRuleGrow('1d', 0.1),
    # TickMakerRuleGrow(span='1d', times=0.01, min_count=3),
    TickMakerRuleMostlyGrow(span='24h', times=0.1, child_span='1h', child_error=0.05),
])
maker.run()

for task in maker.tasks:
    task.save(Path(f'public'))
