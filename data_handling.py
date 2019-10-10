import numpy as np
import pandas as pd
<<<<<<< HEAD

df = pd.read_excel("Data_0.xlsx")
data = pd.DataFrame(df)
amount = 30000
cars = []

for i in range(len(data["SalesPrice"])):
    if(data["Location"].iloc[i] == "DENVER, CO"):
        cars.append(data["SalesPrice"].iloc[i])



string = data["Notes"].iloc[2][:]

for i in range(len(string)):
    string[i]



m = []
for i in range(len(data)):
    string = str(data["Notes"].iloc[i][0:4])
    m.append(string)

print(m)

data["Midi_mini"] = m

data["SalesPrice"].iloc[100:110]
=======
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
>>>>>>> d80b7bb7e39fad50487f6807932370ce4bb8abb6
