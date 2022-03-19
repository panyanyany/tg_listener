import pandas as pd

from tg_listener.repo.arctic_repo import arctic_db

pd.set_option('display.width', 1000)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', None)

print(arctic_db.db_tick.read('0x301ffb3bf647ff04dca945a1f9c9debebc586c26:tick'))
