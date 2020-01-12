import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
# cborn
# time stamp to datetime.datetime
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter
import seaborn as sns
matplotlib.__version__

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
        Year:
            list of years to filter the year the product was made
        Make:
            list of string to filter the product make
        Model:
            list of strings to filter the product model
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

# data = pd.read_excel("../Tractor_Data_Inflation_Adjusted.xlsx", parse_dates=['SaleDate'])
data = pd.read_excel("../Tractor_Data_Inflation_Adjusted.xlsx")
data

fg4 = Filtered_graph(data, range(2012,2017)) # , Location = ["ORLANDO, FL"])
fg4.plot_graph_tot("avg")
fg4.plot_graph_tot()


self = fg4
# fg1 = Filtered_graph(data, SaleDate_Year = [2008, 2009], Location = ["PELZER, SC"], Year = [2005])
# fg1.plot_graph()
# fg1.SaleDate
# fg1.data

#df = df.drop(columns = [ 'Classification', 'Datasource', 'SerialNumber', 'Make', 'AuctionCompany','HP', 'Suspension','Sleeper', 'Trans', 'Spd', 'Axles','TransactionType', 'mNotes'])
df = df.dropna()
fg2 = Filtered_graph(data, SaleDate_Year = [2010], Location = None, SerialNumber = None, Year = None, Make=["FREIGHTLINER"])
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

def get_counts(series):
  X = series.tolist()
  count = Counter(np.array(X))
  tuple_list = count.most_common()
  return tuple_list

most_commons = []
for i in range(data.shape[1]):
    most_commons.append(get_counts(data.iloc[:,i])[0:5])

most_commons


SD1 = None #range(2014,2017) #[2017] #None #[2011]
L1 = ["SOUTH SIOUX CITY NE"] #["ORLANDO, FL"]
SN1 = None
Y1 = [2005]
MA1 = None #["FREIGHTLINER"] #None #["FREIGHTLINER"]
MO1 = ["CL120 COLUMBIA"] #None #["COLUMBIA CL120"]


fg3 = Filtered_graph(data,SaleDate_Year=SD1,Location=L1,SerialNumber=SN1,Year=Y1,Make=MA1,Model=MO1)
fg3.plot_graph()
fg3.plot_graph_tot("avg")

get_counts(fg3.data[fg3.data["Location"] == "SOUTH SIOUX CITY NE"]["Model"])
get_counts(fg3.data["Year"])


SD1 = None #range(2014,2017) #[2017] #None #[2011]
L1 = ["SOUTH SIOUX CITY NE"] #["ORLANDO, FL"]
SN1 = None
Y1 = [2005]
MA1 = None #["FREIGHTLINER"] #None #["FREIGHTLINER"]
MO1 = ["379"] #None #["COLUMBIA CL120"]


fg3 = Filtered_graph(data,SaleDate_Year=SD1,Location=L1,SerialNumber=SN1,Year=Y1,Make=MA1,Model=MO1)
fg3.plot_graph()

# To do:
# Look at the most common datapoint category
# Fix graph format
# Look into binning the data in different ways: See quantity of each month perhaps.
#
# Add the rest of the columns
# Turn this into a GUI
# Data analysis
# Clean up data for this
# Add temperature data
