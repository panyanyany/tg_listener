import sys
from pathlib import Path

import pandas as pd

from tg_listener.repo import tick_maker
from tg_listener.repo.arctic_repo.arctic_repo import arctic_db

pd.set_option('display.width', 1000)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', None)
# pd.set_option('display.max_rows', None)

token = sys.argv[-1]

maker = tick_maker.TickMaker([
    tick_maker.TickMakerTask('15min', 0.1),
])
maker.debug_token = token.lower()
maker.run()

for key in maker.results:
    result = maker.results[key]
    result.save(Path(f'public'))