import pandas as pd

now = pd.datetime.now()
print(now)
print(pd.to_timedelta('1h'))
print(now - pd.to_timedelta('1h'))
