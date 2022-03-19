from datetime import datetime

import dateutil.parser
import pandas as pd
import numpy as np
import pytz
from pandas import Timestamp

from tg_listener.repo.arctic_repo import arctic_db

pd.set_option('display.width', 1000)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', None)
# pd.set_option('display.max_rows', None)


db = arctic_db.db_tick


def filter_token(token):
    stat = arctic_db.get_stat(token)
    last_dt: datetime = stat['last_tick_at']
    diff = (datetime.now() - last_dt).total_seconds() / 60
    if diff > 30:
        return
    data = arctic_db.db_tick.read(f'{token}:tick')
    data = data.resample('15min')['price'].agg(['first', 'last'])
    data['diff'] = (data['last'] - data['first']) / data['first']
    if data.iloc[-1]['diff'] > 0.3:
        print(data.tail())
        print('--- token:', token, stat.get('is_dividend'))

    return

    symbols = arctic_db.db_tick.list_symbols()
    for sym in symbols:
        info = arctic_db.db_tick.get_info(sym)
        if info['len'] > 100:
            print(sym, info)


print(arctic_db.db_tick.read('0x418199ab6e147eb70b22f2317f90e27467009e30:tick'))
exit()

for sym in db.list_symbols(partial_match=':tick'):
    info = db.get_info(sym)
    if info['len'] < 50:
        continue
    token = sym.split(':')[0]
    filter_token(token)
