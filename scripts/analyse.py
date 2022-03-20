import pandas as pd

from tg_listener.repo.arctic_repo import arctic_db

pd.set_option('display.width', 1000)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', None)

token = '0xffd90fcc8c8544e244f0d84c4c83a355ff71328d'

data = arctic_db.db_tick.read(f'{token}:tick')
print(data.tail())
data = data[data['direction'] == 'SELL']
print(len(data))
print(data.tail())

data = arctic_db.db_tick.read(f'{token}:liq:add')
print(data.tail())
data = arctic_db.db_tick.read(f'{token}:liq:remove')
print(data.tail())
