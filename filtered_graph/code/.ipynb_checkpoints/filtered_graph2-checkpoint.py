import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
# cborn
# time stamp to datetime.datetime
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter
# import seaborn as sns
matplotlib.__version__
import os
os.getcwd()

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
        Year:
            list of years to filter the year the product was made
        Make:
            list of string to filter the product make
        Model:
            list of strings to filter the product model
        '''

        self.title = "Price of Every Item Filtered by "
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
        if(self.title == "Price of Every Item Filtered by: "):
            self.title = "Price of Every Item"

        self.data = data
        self.Salesprice = data["Salesprice"].values
        self.SaleDate = data["SaleDate"].values
        # .dt.to_pydatetime()

    def plot_graph_tot(self, graph_type="tot"):
        tot = np.zeros([len(self.SaleDate_Year),12])
        num_datapoint = np.zeros(len(self.SaleDate_Year))
        fig, axes = plt.subplots(len(self.SaleDate_Year), 1, sharex = 'all', sharey='all')
        for j in range(len(self.SaleDate_Year)):
            for i in range(1,13):
                year_df = self.data[self.data["SaleDate"].dt.year == self.SaleDate_Year[j]]
                month_df = year_df[year_df["SaleDate"].dt.month == i]
                # day_df = month_df[month_df["SaleDate"].dt.day == ]
                tot[j, i-1] = np.nansum(month_df["Salesprice"].values)
                if(graph_type == "avg" and tot[j, i-1] != 0):
                    tot[j, i-1] /= len(month_df["Salesprice"])
            if(len(self.SaleDate_Year)==1):
                axes.plot(range(1,13), tot[j,:], color='purple')
            else:
                axes[j].plot(range(1,13), tot[j,:], color='purple')
            num_datapoint[j] = len(year_df)

            # axes[j].set(xlabel="Num datapoint = " + str(len(month_df)))
            # axes[1, 1].plot(range(1,13), tot, '.', color='purple')

        if(graph_type == "avg"):
            title = "Average " + self.title
        else:
            title = self.title
        fig.add_subplot(111, frameon=False)
        plt.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
        plt.xlabel("SalesDate Month")
        plt.grid(False)
        # plt.ylabel("Total Price ($)")
        # plt.yaxis.set_label_position("right")
        plt.title(title)
        plt.savefig('graph.png', dpi=300)
        # fig.tight_layout()

        return num_datapoint
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

    def plot_graph(self, filename=None):
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
        ylabel="Price ($)",
        title=self.title)
        if(filename != None):
            plt.savefig(filename)

data = pd.read_excel("../../../Tractor_Data_Inflation_Adjusted.xlsx")
savefig_path = '../figures/'
savefiles_path = '../files/'

SD = None #range(2014,2017) #[2017] #None #[2011]
L = None #["ORLANDO, FL"]
SN = None
Y = None
MA = None #["FREIGHTLINER"] #None #["FREIGHTLINER"]
MO = None #None #["COLUMBIA CL120"]

# Plot the price of every item in the db
fg1 = Filtered_graph(data,SaleDate_Year=SD,Location=L,SerialNumber=SN,Year=Y,Make=MA,Model=MO)
filename = savefig_path + fg1.title
fg1.plot_graph(filename)

###############################################################################
# Plot the price of every item each individual sale_date year

SD = None #range(2014,2017) #[2017] #None #[2011]
L = None #["ORLANDO, FL"]
SN = None
Y = None
MA = None #["FREIGHTLINER"] #None #["FREIGHTLINER"]
MO = None #None #["COLUMBIA CL120"]

for i in range(1996, 2021):
    SD = [i]
    fg1 = Filtered_graph(data,SaleDate_Year=SD,Location=L,SerialNumber=SN,Year=Y,Make=MA,Model=MO)
    filename = savefig_path + fg1.title
    fg1.plot_graph(filename)

###############################################################################
# Plot the price of every Freightliner item each individual sale_date year

SD = None #range(2014,2017) #[2017] #None #[2011]
L = None #["ORLANDO, FL"]
SN = None
Y = None
MA = ["FREIGHTLINER"] #None #["FREIGHTLINER"]
MO = None #None #["COLUMBIA CL120"]

for i in range(1996, 2021):
    SD = [i]
    fg1 = Filtered_graph(data,SaleDate_Year=SD,Location=L,SerialNumber=SN,Year=Y,Make=MA,Model=MO)
    filename = savefig_path + "1_" + fg1.title
    fg1.plot_graph(filename)

###############################################################################
# Plot the price of every "CL120 COLUMBIA" model for each individual sale_date years
SD = None #range(2014,2017) #[2017] #None #[2011]
L = None #["ORLANDO, FL"]
SN = None
Y = None
MA = None #["FREIGHTLINER"] #None #["FREIGHTLINER"]
MO = ["CL120 COLUMBIA"] #["COLUMBIA CL120"]

for i in range(1996, 2021):
    SD = [i]
    fg1 = Filtered_graph(data,SaleDate_Year=SD,Location=L,SerialNumber=SN,Year=Y,Make=MA,Model=MO)
    filename = savefig_path + "2_" + fg1.title
    fg1.plot_graph(filename)

###############################################################################
# To do:
# - Histogram the data in many small bins... maybe like 100 per year
# (make bin size) changeable by the user. Then look at average price of each bin
# total price of each bin, etc? So basically the user sets the range and the number
# of bins per range.
# - Look at correlations between variables?
