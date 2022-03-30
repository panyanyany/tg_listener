import logging
from pathlib import Path

import pandas as pd

from tg_listener.repo import tick_maker
from tg_listener.repo.arctic_repo.arctic_repo import arctic_db
from util.log_util import setup3, default_ignore_names

setup3(ignore_names=list(set(['web3.*', 'asyncio'] + default_ignore_names) - {'util.*'}))

logger = logging.getLogger(__name__)

pd.set_option('display.width', 1000)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', None)
# pd.set_option('display.max_rows', None)

logger.info('start')

maker = tick_maker.TickMaker([
    tick_maker.TickMakerRuleGrow('15min', 0.1),
    tick_maker.TickMakerRuleGrow('1h', 0.1),
    tick_maker.TickMakerRuleGrow('1h', 0.01, 3),
    tick_maker.TickMakerRuleGrow('1d', 0.1),
    tick_maker.TickMakerRuleGrow('1d', 0.01, 3),
])
maker.run()

for key in maker.results:
    result = maker.results[key]
    result.save(Path(f'public'))
