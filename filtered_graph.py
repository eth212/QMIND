import pandas as pd
import matplotlib.pyplot as plt
# cborn
# time stamp to datetime.datetime
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter

# data = pd.read_excel("../Tractor_Data_Inflation_Adjusted.xlsx", parse_dates=['SaleDate'])
 data = pd.read_excel("../Tractor_Data_Inflation_Adjusted.xlsx")

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
        ylabel="Price ($)",
        title=self.title)

        # self.pivot(index='SaleDate', columns='SalesPrice', values='count').plot(marker='o')


# fg1 = Filtered_graph(data, SaleDate_Year = [2008, 2009], Location = ["PELZER, SC"], Year = [2005])
# fg1.plot_graph()
# fg1.SaleDate
# fg1.data

fg2 = Filtered_graph(data, SaleDate_Year = [2016], Location = None, SerialNumber = None, Year = None, Make=["FREIGHTLINER"])
fg2.plot_graph()


# To do:
# Look into binning the data in different ways: See quantity of each month perhaps.
#
# Add the rest of the columns
# Turn this into a GUI
# Data analysis
