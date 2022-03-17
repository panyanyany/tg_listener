import numpy as np
import pandas
import pandas as pd
from pandas import MultiIndex, DataFrame, Index
from datetime import datetime as dt

from tg_listener.repo.arctic_repo import arctic_db

data = arctic_db.lib.delete('0x69b14e8d3cebfdd8196bfe530954a0c226e5008e:tick',
                            chunk_range=pd.date_range('2022-03-17 09:51:01', '2022-03-17 09:51:16', freq='S'))
data = arctic_db.lib.read('0x69b14e8d3cebfdd8196bfe530954a0c226e5008e:tick')
print(data.head())
