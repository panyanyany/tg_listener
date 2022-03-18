import numpy as np
import pandas
import pandas as pd
from pandas import MultiIndex, DataFrame, Index
from datetime import datetime as dt

from tg_listener.repo.arctic_repo import arctic_db

pd.set_option('display.width', 1000)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', None)

for sym in arctic_db.db_tick.list_symbols():
    if 'liq' not in sym:
        continue

    print(arctic_db.db_tick.read(sym))
    print(sym)
