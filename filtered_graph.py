import pandas as pd
import matplotlib.pyplot as plt
# cborn
# time stamp to datetime.datetime

data = pd.read_excel("../Tractor_Data_Inflation_Adjusted.xlsx")
data

class Filtered_graph:
    def __init__(self, data, Year=None):
        self.Salesprice = data["Salesprice"].values
        self.SaleDate = data["SaleDate"].values
        if(Year != None):
            self.Year = Year
            self.data = data[data["Year"]==Year]

    def plot_graph(self):
        plt.plot(self.SaleDate, self.Salesprice, ".")
        plt.xlabel("Time")
        plt.ylabel("Price")
        plt.title("Price of Every Item with: year =" + str(self.Year))
        plt.show()


fg1 = Filtered_graph(data, 2000)
fg1.plot_graph()
