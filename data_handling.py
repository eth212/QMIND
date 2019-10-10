import numpy
import pandas as pd

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
