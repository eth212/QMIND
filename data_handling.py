import numpy as np
import pandas as pd

big_data = pd.read_excel("tractor/tractor_data.xlsx")
df = pd.DataFrame(big_data)
df.corrwith(df["Salesprice"])
def make_col():
    days_since = []
    value_check = pd.notnull(df["Year"])
    for i in range(len(df["SaleDate"])):
        if value_check.iloc[i]:
            day = df["SaleDate"].iloc[i].dayofyear
            year_sold = df["SaleDate"].iloc[i].year
            make_year = int(df["Year"].iloc[i])
            value = (year_sold - make_year) + day
            days_since.append(value)
        else:
            days_since.append(0)
    return days_since

list_dates = make_col()

df["DaysOwned"] = list_dates
df2 = pd.DataFrame()
