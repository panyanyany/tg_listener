import pandas as pd

from tg_listener.repo.arctic_repo import arctic_db

pd.set_option('display.width', 1000)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', -1)


data = arctic_db.db_tick.read('0x00e1656e45f18ec6747f5a8496fd39b50b38396d:tick')
with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    print(data[data['price'] > 21])
data = data.resample('15min')['price'].agg(['first', 'last'])
data['diff'] = 100 * (data['last'] - data['first']) / data['first']
print(data)
exit()

symbols = arctic_db.db_tick.list_symbols()
for sym in symbols:
    info = arctic_db.db_tick.get_info(sym)
    if info['appended_rows'] > 200:
        print(sym, info)
