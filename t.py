import numpy as np
import pandas as pd

dates = pd.date_range('2022-01-01', '2022-02-01')
df = pd.DataFrame(np.random.randn(6, 4), columns=list('ABCD'), index=dates[:6])
print(df)
