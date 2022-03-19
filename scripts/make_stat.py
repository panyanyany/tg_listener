import pandas as pd
import numpy as np

from tg_listener.repo.arctic_repo import arctic_db

pd.set_option('display.width', 1000)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', None)

db = arctic_db.db_tick


def filter_token(token):
    data = arctic_db.db_tick.read(f'{token}:tick')
    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    #     print(data.loc['2022-03-18 06:50:00':'2022-03-18 06:59:59'])
    # exit()
    data = data.resample('15min')['price'].agg(['first', 'last'])
    data['diff'] = (data['last'] - data['first']) / data['first']
    if data.iloc[-1]['diff'] > 0.2:
        print(data)
        print('--- token:', token)
    return

    symbols = arctic_db.db_tick.list_symbols()
    for sym in symbols:
        info = arctic_db.db_tick.get_info(sym)
        if info['len'] > 100:
            print(sym, info)


# print(arctic_db.db_tick.read('0x93dfa1613e47da016a937e26cce6626015e83407:liq:remove'))
# exit()

for sym in db.list_symbols(partial_match=':tick'):
    info = db.get_info(sym)
    # print(sym, info)
    if info['len'] < 50:
        continue
    token = sym.split(':')[0]
    filter_token(token)
