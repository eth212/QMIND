import numpy
import pandas as pd
use_cols = [i for i in range(27)]
df = pd.read_csv("Data_0.csv",header=0,usecols=use_cols)
