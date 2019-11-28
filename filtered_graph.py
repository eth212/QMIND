import pandas as pd
import matplotlib.pyplot as plt
# cborn
# time stamp to datetime.datetime

# data = pd.read_excel("../Tractor_Data_Inflation_Adjusted.xlsx", parse_dates=['SaleDate'])
 data = pd.read_excel("../Tractor_Data_Inflation_Adjusted.xlsx")

class Filtered_graph:
    def __init__(self, data, SaleDate_Year=None, Year=None):

        if(SaleDate_Year != None):
            self.SaleDate_Year = SaleDate_Year
            data = data[data["SaleDate"].dt.year==SaleDate_Year]
        if(Year != None):
            self.Year = Year
            data = data[data["Year"]==Year]
        self.data = data
        self.Salesprice = data["Salesprice"].values
        self.SaleDate = data["SaleDate"].dt.to_pydatetime()

    def plot_graph(self):
        plt.plot(self.SaleDate, self.Salesprice, ".")
        plt.xlabel("Time")
        plt.ylabel("Price")
        # plt.title("Price of Every Item with: year =" + str(self.Year))
        plt.show()
        # self.pivot(index='SaleDate', columns='SalesPrice', values='count').plot(marker='o')

fg1 = Filtered_graph(data, 2017, 2011)
fg1.plot_graph()
fg1.data
