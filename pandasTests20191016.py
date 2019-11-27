import pandas as pd
print("hello world")
use_cols = [i for i in range(27)]
df = pd.read_excel("Data_0.xlsx",header=0,usecols=use_cols)
df
type(df)
df['Notes'][0:20]
