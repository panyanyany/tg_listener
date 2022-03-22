from datetime import datetime, timedelta

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


def filter_token(stat, token, times=0.5, span='30min'):
    # stat = arctic_db.get_stat(token)
    # last_dt: datetime = stat['last_tick_at']
    # idle = (datetime.now() - last_dt).total_seconds() / 60
    # if idle > 15:
    #     return
    data = arctic_db.db_tick.read(f'{token}:tick')
    if len(data[data['direction'] == 'SELL']) < 3:
        return
    # print(data[['price', 'hash', 'value']].tail())
    # print(token)
    data = data.resample(span)['price'].agg(['first', 'last'])
    data['diff'] = (data['last'] - data['first']) / data['first']
    if data.iloc[-1]['diff'] > times:
        print(data.tail())
        print(f'--- token: https://poocoin.app/tokens/{token}', stat.get('is_dividend'), stat['pools'])

    return

    symbols = arctic_db.db_tick.list_symbols()
    for sym in symbols:
        info = arctic_db.db_tick.get_info(sym)
        if info['len'] > 100:
            print(sym, info)


# 开盘时间最小允许多久(min)
open_min_age = 60
# 空闲期(上一次交易到现在)最大允许多久(min)
idle_max_span = 15

dt_idle_gte = datetime.now() - timedelta(minutes=idle_max_span)
dt_open_lte = datetime.now() - timedelta(minutes=open_min_age)
query = {"last_tick_at": {"$gte": dt_idle_gte},
         "recorded_at": {"$lte": dt_open_lte}}
stats = arctic_db.db_data.stats.find(query)

# print(stats.count())
# print(len(db.list_symbols(partial_match=':tick')))
# exit()

for stat in stats:
    sym = f"{stat['token']}:tick"
    if not db.has_symbol(sym):
        continue
    info = db.get_info(sym)
    if info['len'] < 5:
        continue
    token = sym.split(':')[0]
    filter_token(stat, token, span='1h', times=0.5)
