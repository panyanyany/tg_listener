import numpy as np
import pandas
import pandas as pd
from pandas import MultiIndex, DataFrame, Index
from datetime import datetime as dt

from tg_listener.repo.arctic_repo import arctic_db

df = DataFrame(data={'data': [1, 2, 3]},
               index=Index([dt(2016, 1, 1, 1, 1, 1),
                            dt(2016, 1, 2, 1, 1, 2),
                            dt(2016, 1, 3, 2, 1, 3), ],
                           name='date'))

arctic_db.lib.append('test', df, upsert=True)

df = DataFrame(data={'data': [1, 2, 3]},
               index=Index([dt(2016, 1, 1, 1, 1, 11),
                            dt(2016, 1, 2, 1, 1, 22),
                            dt(2016, 1, 3, 2, 1, 33), ],
                           name='date'))
arctic_db.lib.append('test', df, upsert=True)
print(arctic_db.lib.read('test'))
print(arctic_db.lib.get_info('test'))
