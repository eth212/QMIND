import pandas as pd
import matplotlib.pyplot as plt
# cborn
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter
import numpy as np

# data = pd.read_excel("../Tractor_Data_Inflation_Adjusted.xlsx", parse_dates=['SaleDate'])

data = pd.read_excel("tractor/Tractor_Data_Inflation_Adjusted.xlsx")
df = pd.DataFrame(data)

class Filtered_graph:
    def __init__(self, data, SaleDate_Year=None, Location=None, SerialNumber=None, Year=None, Make=None, Model=None):
        '''
        data:
            pandas dataframe formatted like Tractor_Data_Inflation_Adjusted
        SaleDate_Year:
            list of years to filter the SaleDate
        Location:
            list of strings of the form "(city, state)" to filter the location
        SerialNumber:
            list of strings to filter the SerialNumber
        Make:
            list of string to filter the product make
        Model:
            list of strings to filter the product model
        Year:
            list of years to filter the year the product was made
        '''

        self.title = "Price of Every Item Filtered by: "
        if(SaleDate_Year != None):
            self.SaleDate_Year = SaleDate_Year
            data = data[data["SaleDate"].dt.year.isin(SaleDate_Year)]
            self.title += "SaleDate_Year = " + str(SaleDate_Year) + ", "
        if(Location != None):
            self.Location = Location
            data = data[data["Location"].isin(Location)]
            self.title += "Location = " + str(Location) + ", "
        if(SerialNumber != None):
            self.SerialNumber = SerialNumber
            data = data[data["SerialNumber"].isin(SerialNumber)]
            self.title += "SerialNumber = " + str(SerialNumber) + ", "
        if(Year != None):
            self.Year = Year
            data = data[data["Year"].isin(Year)]
            self.title += "Year = " + str(Year) + ", "
        if(Make != None):
            self.Make = Make
            data = data[data["Make"].isin(Make)]
            self.title += "Make = " + str(Make) + ", "
        if(Model != None):
            self.Model = Model
            data = data[data["Model"].isin(Model)]
            self.title += "Model = " + str(Model) + ", "

        self.data = data
        self.Salesprice = data["Salesprice"].values
        self.SaleDate = data["SaleDate"].values
        # .dt.to_pydatetime()

    def plot_graph_tot(self, graph_type="tot"):
        tot = np.zeros([len(self.SaleDate_Year),12])
        fig, axes = plt.subplots(len(self.SaleDate_Year), 1, sharex = 'all', sharey='all')
        for j in range(len(self.SaleDate_Year)):
            for i in range(1,13):
                year_df = self.data[self.data["SaleDate"].dt.year == self.SaleDate_Year[j]]
                month_df = year_df[year_df["SaleDate"].dt.month == i]
                # day_df = month_df[month_df["SaleDate"].dt.day == ]
                tot[j, i-1] = np.nansum(month_df["Salesprice"].values)
                if(graph_type == "avg" and tot[j, i-1] != 0):
                    tot[j,i-1] /= len(month_df["Salesprice"])
            axes[j].plot(range(1,13), tot[j,:], color='purple')
            title = self.title + "Num datapoint = " + str(len(month_df))
            # axes[j].set(xlabel="Sales Month",
            # ylabel="Total Price Sold ($)",
            # title=title)
            # axes[1, 1].plot(range(1,13), tot, '.', color='purple')

            fig.add_subplot(111, frameon=False)
            plt.xlabel("SalesDate Month")
            plt.ylabel("Total Price ($)")
            plt.title(self.title)

        # fig, ax = plt.subplots(figsize=(9, 7))
        # ax.plot(range(1,13),
        # tot, '.',
        # color='purple')
        # ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
        # ax.xaxis.set_major_formatter(DateFormatter("%m/%d")
        # locator = mdates.AutoDateLocator()
        # formatter = mdates.ConciseDateFormatter(locator)
        # ax.xaxis.set_major_locator(locator)
        # # ax.xaxis.set_major_formatter(formatter)
        # axes[0].set(xlabel="Sales Month",
        # ylabel="Total Price Sold ($)",
        # title=self.title)

    def plot_graph(self):
        # plt.plot(self.SaleDate, self.Salesprice, ".")
        # plt.xlabel("Time")
        # plt.ylabel("Price")
        # plt.title(self.title)
        # plt.show()
        fig, ax = plt.subplots(figsize=(9, 7))
        ax.plot(self.SaleDate,
        self.Salesprice, '.',
        color='purple')
        # ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
        # ax.xaxis.set_major_formatter(DateFormatter("%m/%d")
        locator = mdates.AutoDateLocator()
        formatter = mdates.ConciseDateFormatter(locator)
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(formatter)
        ax.set(xlabel="SaleDate",
        ylabel="Price ($)", title=self.title)

        # self.pivot(index='SaleDate', columns='SalesPrice', values='count').plot(marker='o')



fg4 = Filtered_graph(data, range(2012,2017), Location = ["ORLANDO, FL"])
fg4.plot_graph_tot("avg")
fg4.plot_graph_tot()


self = fg4
# fg1 = Filtered_graph(data, SaleDate_Year = [2008, 2009], Location = ["PELZER, SC"], Year = [2005])
# fg1.plot_graph()
# fg1.SaleDate
# fg1.data

fg2 = Filtered_graph(data, SaleDate_Year = [2009], Location = ["ORLANDO, FL"], SerialNumber = None, Year = None, Make=["FREIGHTLINER"], Model=["COLUMBIA CL120"])
fg2.plot_graph()

SD1 = [2015] #None #[2011]
L1 = None #["ORLANDO, FL"]
SN1 = None
Y1 = None
MA1 = ["FREIGHTLINER"] #None #["FREIGHTLINER"]
MO1 = ["COLUMBIA CL120"] #None #["COLUMBIA CL120"]

fg3 = Filtered_graph(data,SaleDate_Year=SD1,Location=L1,SerialNumber=SN1,Year=Y1,Make=MA1,Model=MO1)
fg3.plot_graph()

fg4 = Filtered_graph(data, [2015])
fg4.plot_graph()
fg4.plot_graph_tot()

fg4.data

tot = np.zeros(12)
for i in range(1,13):
    month_df = fg4.data[fg4.data["SaleDate"].dt.month == i]
    tot[i-1] = np.nansum(month_df["Salesprice"].values)

tot[0]


# To do:
# Total price of everything sold per month graph, average
# Output how many datapoints are used to make the graph
# Look into binning the data in different ways: See quantity of each month perhaps.
# Change the colour data points
# Make a function to so you can look at all data in a certain state or certain area
# Add the rest of the columns
# Turn this into a GUI
# Data analysis
