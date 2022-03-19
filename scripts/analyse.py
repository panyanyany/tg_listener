import pandas as pd

from tg_listener.repo.arctic_repo import arctic_db

pd.set_option('display.width', 1000)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', None)

print(arctic_db.db_tick.read('0x9d4451151a8de5b545a1bc6c8fdeb9d94a2868e1:tick'))
