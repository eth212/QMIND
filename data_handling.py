import numpy as np
import pandas as pd
use_cols = [i for i in range(27)]
df = pd.read_excel("Data_0.xlsx",header=0,usecols=use_cols)

#num_2012 = len([i for i in df['Year'] if i==2012])
#print(num_2012)

def separate_commas(dataframe,column):
    column_data = dataframe[column]
    column_better = []
    for datapoint in column_data:
        words = [""]
        count = 0
        for letter in datapoint:
            if letter!=",":
                words[count]+=letter
            else:
                words.append("")
                count+=1
        column_better.append(words)
    dataframe[column]=column_better
separate_commas(df,"Notes")
