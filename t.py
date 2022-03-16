import numpy as np
import pandas
import pandas as pd

from tg_listener.repo.arctic_repo import arctic_db

print(arctic_db.lib.list_symbols())
for s in arctic_db.lib.list_symbols():
    # arctic_db.lib.delete(s)
    # continue
    data = arctic_db.lib.read(s)
    print(data)
    # if len(data) < 50:
    #     continue
    # print(s, len(data))
