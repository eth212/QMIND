from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
import pyodbc
import pandas as pd
import json
import ast
import numpy as np
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
from pytrends.request import TrendReq
import plotly as py
from geopy import geocoders
py.tools.set_credentials_file(
	username='jeremykulchyk', api_key='ZNb8x0IBYP7SCQFiaf9T')
pytrend = TrendReq(hl='en-US', tz=360)
gn = geocoders.GeoNames(username='13jjrk')

# Dict of months
MList = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
		 7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}

cnxn = pyodbc.connect('DRIVER=FreeTDS;SERVER=localhost;PORT=1433;DATABASE=QMIND;UID=sa;PWD=reallyStrongPwd123;TDS_Version=8.0;')
# cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER=192.168.99.100;PORT=1433;UID=sa;PWD=Qmind2020!;TDS_Version=8.0;')

# Load index.html on searching servername +'/dashboard/'


def index(request):
	with open("dashboard/static/dashboard/us-states.json") as geoJSON:
		us_states = json.load(geoJSON)

	df = pd.read_csv("dashboard/static/dashboard/csv/All_Locations_LongLat.csv")
	city_coords = {}
	for i, city in enumerate(df['Location'].dropna()):
		noComma = city.replace(',', '')
		if noComma not in city_coords.keys():
			city_coords[noComma] = [df['Latitude'][i], df['Longitude'][i]]
	# city_coords = {'city': df['Location'].tolist(), 'lat': df['Latitude'].tolist(), 'long': df['Longitude'].tolist()}
	return render(request, 'dashboard/index.html', context={'us_states': us_states, 'city_coords': json.dumps(city_coords)})

# Update the Google Search trend data when the user clicks a related search term or custom searches their own


def updateSearchTerm1(request):
	if request.method == 'GET':
		# Get search term
		item1 = request.GET['NewSearchTerm']

		# Static list of State codes to be added as column in PytrendsTerm1.csv. This is done so that plotly.js can find the states location on the map generated
		Codes = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS',
				 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY']
		# Setup Codes as pandas dataframe column
		se = pd.Series(Codes)

		# Build google search trends payload, and save interest_over_time dataframe to csv file
		pytrend.build_payload(
			kw_list=[item1.lower()], geo='US', timeframe='today 12-m')
		interest_over_time_df = pytrend.interest_over_time()
		interest_over_time_df.to_csv(
			"dashboard/static/dashboard/csv/PytrendsTerm1Interest.csv")

		# Get interest_by_region dataframe, remove District of Columbia since plotly.js's scattergeo plot doesn't use it
		interest_by_region_df = pytrend.interest_by_region()
		interest_by_region_df = interest_by_region_df[interest_by_region_df.index !=
													  "District of Columbia"]
		# Add state codes as column in interest_by_region_df
		interest_by_region_df['code'] = se.values
		# Save df to csv
		interest_by_region_df.to_csv(
			"dashboard/static/dashboard/csv/PytrendsTerm1.csv")
		print(interest_by_region_df)

		# Return search term to html file script titled: Search term 1 Custom Search, or Search term 1 Related Search
		data_details = {'item1': item1.lower()}
		return JsonResponse(data_details)

	return render(request)

# Get Google Trend data and save to csv file to be used by plotly in the index.html file script titled: Search term 1 Custom Search, or Search term 1 Related Search, or Get Results


def getGoogleTrends(request):
	if request.method == 'GET':

		# Store users selected values from each dropdown list
		Category = request.GET['Cat']
		Dutytype = request.GET['Duty']
		Make = request.GET['Make']
		Model = request.GET['Model']
		Year = request.GET['Year']

		# Possible search queries, based on selector. Default selector as 1. Search queries start specific and get more general to ensure trend data is found
		Selector = 1
		SearchQueries = {1: ['used ' + Make + ' ' + Dutytype,
							 'used ' + Make + ' ' + Category,
							 Make + ' ' + Dutytype + ' for sale',
							 Make + ' ' + Category,
							 'used ' + Make,
							 'used ' + Dutytype,
							 'used ' + Category],
						 2: ['used ' + Dutytype,
							 Dutytype + ' for sale',
							 'used ' + Category,
							 Category + ' for sale'],
						 3: ['used ' + Category,
							 Category + ' for sale']}

		# Choose selector based on what data the user has selected from the Data Entry dropdown lists
		if Category != "" and Dutytype != "" and Make != "":
			Selector = 1
		if Category != "" and Dutytype != "" and Make == "":
			Selector = 2
		if Category != "" and Dutytype == "" and Make == "":
			Selector = 3

		# Declare interest_over_time_df and interest_by_region_df out of for loop scope for use outside of for loop scope
		interest_over_time_df = None
		interest_by_region_df = None

		# Try building payloads for search queries. If search trend data is all 0's, keep searching. Otherwise, Flag is set to True and for loop breaks.

		# Only care about interest_by_region to find available data; if there is interest_by_region data available, there will always
		# 	be interest_over_time data available, but not vice versa
		for SI in SearchQueries[Selector]:
			pytrend.build_payload(
				kw_list=[SI.lower()], geo='US', timeframe='today 12-m')
			interest_by_region_df = pytrend.interest_by_region()
			print(interest_by_region_df)
			flag = False
			for index, rows in interest_by_region_df.iterrows():
				if interest_by_region_df.loc[index][0] != 0:
					flag = True
			if flag == True:
				print(SI)
				item1 = SI
				break

		# Now that interest_by_region is set, payload is already built, so find interest_over_time_df
		interest_over_time_df = pytrend.interest_over_time()

		# Static list of State codes to be added as column in PytrendsTerm1.csv. This is done so that plotly.js can find the states location on the map generated
		Codes = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS',
				 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY']
		# Setup Codes as pandas dataframe column
		se = pd.Series(Codes)

		# Save interest_over_time dataframe to csv file
		interest_over_time_df.to_csv(
			"dashboard/static/dashboard/csv/PytrendsTerm1Interest.csv")

		# Get interest_by_region dataframe, remove District of Columbia since plotly.js's scattergeo plot doesn't use it
		interest_by_region_df = interest_by_region_df[interest_by_region_df.index !=
													  "District of Columbia"]
		# Add state codes as column in interest_by_region_df
		interest_by_region_df['code'] = se.values
		# Save df to csv
		interest_by_region_df.to_csv(
			"dashboard/static/dashboard/csv/PytrendsTerm1.csv")

		# Get related queries and store in dictionary
		related_queries_dict = pytrend.related_queries()

		# Add top related queries to html formatted string
		try:
			ListData1 = ""
			for keys in related_queries_dict:
				ListData1 = ListData1 + "<h4>Top Related Searches</h4><br>"
				for items in related_queries_dict[keys]['top']['query']:
					ButtonItem = '<button type="button" class="btn btn-link" id="ChangeSearchTerm1">%s</button>' % (
						items)
					ListData1 = ListData1 + ButtonItem
		except:
			# If problems arise, don't show related queries
			ListData1 = ""

		# return search keyword as 'item1' and related search queries as myDiv13, which is the id of the div in index.html that will display the related searches
		data_details = {'item1': item1.lower(), 'myDiv13': ListData1}
		return JsonResponse(data_details)

	return render(request)


# Helper function used in get_results, and hist_go
# To Do:
# Could change the colours of the boxplot the same way
# Add a loading bar that stops only once the csv is actually ready
# Sometimes the server still gets out of sync
# Put the box and whisker plot first??
def write_hist_data(Data, highlight_year=None, HistDataLocations=None):
	Data.to_csv("dashboard/static/dashboard/csv/HistData.csv", columns=["SaleDate","SalesPrice", "YearMonth"])
	if(type(HistDataLocations) != type(None)):
		Data = Data[Data["Location"] == HistDataLocations]
		Data.to_csv("dashboard/static/dashboard/csv/HistData.csv", columns=["SaleDate","SalesPrice", "YearMonth"])
	# Make a second csv with just a single years worth of data, to turn a different colour upon a change in the map slider
	if(type(highlight_year) != type(None)):
		single_year = Data[Data['SaleDate'].dt.year==highlight_year]
		single_year.to_csv("dashboard/static/dashboard/csv/HistData_single_year.csv", columns=["SaleDate","SalesPrice", "YearMonth"])
	else: # If no year is supplied highlight all the data
		Data.to_csv("dashboard/static/dashboard/csv/HistData_single_year.csv", columns=["SaleDate","SalesPrice", "YearMonth"])

	data = Data.drop(columns=["Location", "SaleDate", 'DutyType', 'Source', 'CreatedTime', 'ModifiedTime', 'AssetID',
'SerialNumber', 'Year', 'Make', 'Model', 'AuctionCompany',
'Mileage', 'Engine', 'HP', 'Suspension', 'Sleeper', 'Trans', 'Spd',
'Axles', 'TransactionType', 'Notes'])
	# print(data.columns)
	# print(data.head())
	unique_yearmonths = np.sort(data.YearMonth.unique())
	n_unique_yearmonths = [] # Number of datapoints per box

	i = 0
	df1 = data[data["YearMonth"] == unique_yearmonths[i]]
	df1 = df1.reset_index(drop=True)
	df1 = df1.drop(columns = ['YearMonth'])
	n_unique_yearmonths.append(str(len(df1)))
	for i in range(1, len(unique_yearmonths)):
		df2 = data[data["YearMonth"] == unique_yearmonths[i]]
		df2 = df2.reset_index(drop=True)
		df2 = df2.drop(columns = ['YearMonth'])
		n_unique_yearmonths.append(str(len(df2)))
		df = [df1, df2]
		df_final = pd.concat(df, axis = 1, ignore_index = True)
		df1 = df_final
	df_final.to_csv("dashboard/static/dashboard/csv/BoxData.csv", index=False)

	# Try turning into df and then writing to file
	# pd.DataFrame(np.array([np.append(["yearmonths"], unique_yearmonths), np.append(["n_yearmonths"], n_unique_yearmonths)], dtype = str).T).to_csv("dashboard/static/dashboard/csv/BoxDataColumns.csv")
	# print(unique_yearmonths)
	df_final_cols = pd.DataFrame(np.vstack([unique_yearmonths, n_unique_yearmonths]).T, columns = ["yearmonths", "nyearmonths"])
	# print(df_final_cols.head())
	df_final_cols.to_csv("dashboard/static/dashboard/csv/BoxDataColumns.csv")

	# pd.DataFrame(np.array([unique_yearmonths, unique_yearmonths], dtype = str).T, columns = ["yearmonths", "nyearmonths"]).to_csv("dashboard/static/dashboard/csv/BoxDataColumns.csv")

	# np.savetxt("dashboard/static/dashboard/csv/BoxDataColumns.csv", np.array([np.append(["yearmonths"], unique_yearmonths), np.append(["n_yearmonths"], n_unique_yearmonths)], dtype = str).T, '%s', delimiter=",")


# (MAIN FUNCTION) Get data from database, filter data, sort data by location, attach metrics to each location, format data to HTML table rows.


def getData(request):

	# Rank Function for sorting dictionary by avgprice, totalrev,.. etc.
	def RankMap(dictt, string, Reverse):
		Ranked = sorted(
			dictt.items(), key=lambda x: x[1][string], reverse=Reverse)
		print(Ranked)
		return Ranked

	if request.method == 'GET':

		# Store user selected data into variables
		Category = request.GET['Cat']
		Dutytype = request.GET['Duty']
		Make = request.GET['Make']
		Model = request.GET['Model']
		Year = request.GET['Year']
		YearRangeEnd = request.GET['YearRangeEnd']
		IncludeAllData = request.GET['IncludeMileage']
		UseTable = request.GET['UseTable']

		print(Year, YearRangeEnd)

		# If the year selected is less than the end year for the year range, swap their values to keep sql query happy
		if YearRangeEnd != "":
			if Year > YearRangeEnd:
				temp = Year
				Year = YearRangeEnd
				YearRangeEnd = temp

			# If the year selected is the same as the end year for the year range, just pretend it's only 1 year being asked for
			if Year == YearRangeEnd:
				YearRangeEnd = ""

		# If the user only selects data from the Category, and dutytype dropdown lists, return a Too General message since too much data will be retrieved from database, possibly causing crash.
		if Make == "" and Model == "" and Year == "" and YearRangeEnd == "":
			data_details = {'Error': 'TooGeneral'}
			return JsonResponse(data_details)

		# Setup SQL database connection, which is powered by pydobc.
		# NOTE: pyodbc was downloaded and its instructions were followed in order to access the database from my laptop, through any python program, through the same network.
		#cnxn = pyodbc.connect('DSN=MYMSSQL;UID=sa;PWD=Q1w2e3r4t5y6u7i8o9p0')

		"""
		# Use the user's selected category (which is the categories display name) to find the categories actual database name, which is under the column DutyTypeDesc in the below query
		sql1 = "SELECT * FROM QMIND.dbo.DBDutyType where ParentDutyTypeID is null"
		Data1 = pd.read_sql(sql1,cnxn)
		print(Data1)
		df = Data1.loc[Data1['DisplayName'] == Category]
		Category = df['DutyTypeDesc'].iloc[0]
		"""

		# This section uses the below SQL variables to dynamically create a SQL query, based on the data selected from the dropdown menu
		DB = "QMIND.dbo."
		SF = "SELECT * FROM "
		W = " where "
		D = "DUTYTYPE = '"
		M = "MODEL = '"
		MA  = "MAKE = '"
		Y = "YEAR = '"
		E = "'"
		A = " AND "
		# Start by assignment variable to None to add to namespace
		sql = None

		# The following 4 if statements work backwards to generate the correct SQL query statement.
		#if Year == "":
		sql = SF + DB + Category + W + D + Dutytype + E + A + MA + Make + E + A + M + Model + E
		if Model == "":
			sql = SF + DB + Category + W + D + Dutytype + E + A + MA + Make + E
		if Make == "":
			sql = SF + DB + Category + W + D + Dutytype + E
		if Dutytype == "":
			sql = SF + DB + Category

		#if Model != "" and Dutytype !== and Make != "":
			#sql = SF + DB + Category + W + D + Dutytype + E + A + MA + Make + E + A + M + Model + E

		# The following 2 if statements then extend the SQL statement if a year or year range is selected.
		# Within each if statement, they differ by the dutytype being null valued, which requires a 'WHERE' to follow, or valued, which requires an 'AND' to follow since 'WHERE' is already present in the SQL query statement
		if Year != "" and YearRangeEnd == "":
			print(sql, W, Y, Year, E)
			if Year != "" and Dutytype == "":
				sql = sql + W + Y + Year + E
			if Year != "" and Dutytype != "":
				sql = sql + A + Y + Year + E
		if Year != "" and YearRangeEnd != "":
			if Year != "" and Dutytype == "":
				sql = sql + W + "Year BETWEEN " + Year + A + YearRangeEnd
			if Year != "" and Dutytype != "":
				sql = sql + A + "Year BETWEEN " + Year + A + YearRangeEnd

		# Execute SQL statement
		print(sql)
		Data = pd.read_sql(sql,cnxn)
		print("length: %s" %len(Data))

		# This is the number of rows before the data is filtered
		DataRowsB = len(Data)

		# See what column headers the data contains
		print(Data.columns)

		# If IncludeAllData is true, that means any row that contains a 0 or is null values will be dropped.
		# The below try statement uses a nested try/except algorithm to select the correct column headers.
		# The data is consistent across all column headings except for hours, mileage, and reefer hours.
		# The below try statement tries to pull the sql data into a pandas dataframe, and if it fails that means the hours,
		# mileage, or reeferhours, is not a column heading in the selected data
		if IncludeAllData == 'true':
			try: # See if hours is in columns
				df = Data[['DutyType','AuctionCompany','Make','Model','SaleDate','Year','Location','SalesPrice','Hours']]
				df = df[df.Hours.notnull()]
				df = df[(df.Hours != '0')]
				df = df[(df.Hours != 'NULL')]
				df = df[(df.Hours != 'None')]
			except: # Hours not in columns
				try: # See if Mileage is in columns
					df = Data[['DutyType','AuctionCompany','Make','Model','SaleDate','Year','Location','SalesPrice','Mileage']]
					df = df[df.Mileage.notnull()]
					df = df[df.Mileage != '0']
					df = df[(df.Mileage != 'NULL')]
					df = df[(df.Mileage != 'None')]
				except: # Mileage not in columns
					try: # See if ReeferHours is in columns
						df = Data[['DutyType','AuctionCompany','Make','Model','SaleDate','Year','Location','SalesPrice','ReeferHours']]
						df = df[df.ReeferHours.notnull()]
						df = df[df.ReeferHours != '0']
						df = df[(df.ReeferHours != 'NULL')]
						df = df[(df.ReeferHours != 'None')]
					except: # ReeferHours not in columns
						# Don't include hours, mileage, or reefer hours.
						df = Data[['DutyType','AuctionCompany','Make','Model','SaleDate','Year','Location','SalesPrice']]
			# Always drop rows with null valued years. The number of rows that have null valued years will typically be < 5%.
			# Hours/mileage/reeferhours on the other hand - sometimes the number of rows that don't contain this data is 100%.
			# This is why there is the option to select or deselect IncludeAllData. In index.html, this selector is just called
			# the Mileage/Hours selector, since it really only pertains to this column heading.
			df = df[df.Year.notnull()]

		# The below code will run for IncludeAllData == 'False', which does the same nested try/excepts, but doesn't drop any
		# rows null values in certain columns. This typically allows for a lot more data to be analyzed.
		else:
			try:
				df = Data[['DutyType','AuctionCompany','Make','Model','SaleDate','Year','Location','SalesPrice','Hours']]
			except:
				try:
					df = Data[['DutyType','AuctionCompany','Make','Model','SaleDate','Year','Location','SalesPrice','Mileage']]
				except:
					try:
						df = Data[['DutyType','AuctionCompany','Make','Model','SaleDate','Year','Location','SalesPrice','ReeferHours']]
					except:
						df = Data[['DutyType','AuctionCompany','Make','Model','SaleDate','Year','Location','SalesPrice']]
			# Always drop rows with null valued years. The number of rows that have null valued years will typically be < 5%.
			df = df[df.Year.notnull()]

		# This is the number of rows after the data is filtered
		DataRowsA = len(df)
		print(len(df))

		# If there is no data after the data filter, return a NoData error.
		if len(df) == 0:
			data_details = {'Error' :'NoData'}
			return JsonResponse(data_details)

		# See filtered data in console
		print(df)

		# The table can be quite slow, so it is now an option whether or not to use it (select the UseTable checkbox)
		if UseTable == 'true':
			# Sort values in dataframe alphabetically by location.
			Loc = df.sort_values('Location')['Location']

			# Locs is a dictionary that has each key as a location, and uses the df to calculate a set of metrics for each location.
			Locs = {}
			LocsYear = {}

			for items in Loc:
				try:
					LocsYear[items] = {}
				except:
					continue

			for keys in LocsYear:
				try:
					LocsYear[keys] = []
				except:
					continue


			# For Each location in the Loc dataframe, initialize each location as a key with the below dictionary as its value.
			# This means each location is a key in Locs, and each key in Locs has the same set of keys as listed below.
			for items in Loc:
				try:
					Locs[items] = {'MostRevMonth':[],'HighSaleMonth':[],'TotalRev':0,'HighSale':0,'LowSale':0,'AvgAge':0,'AvgPrice':0,'AvgMil':0,'SoldAssets':0,'long':0,'lat':0}
				except:
					continue

			# Open the LocsGPS.txt file, which is a dictionary for each locations lat and long. This speeds up the process,
			# since it doesn't rely on the network to find these coordinates.
			with open("dashboard/static/dashboard/csv/LocsGPS.txt",'r') as inf:
				GPSdict = eval(inf.read())

			# This is the main for loop that calculates all the metrics for each location.
			for keys in Locs:
				# Display location in console
				print(keys)

				# Months is a dictionary of months as keys, which each point to a list of two numbers: Highest Sale Price, Lowest Sale Price
				# For now they are initialized as 0.
				Months = {1:[0,0],2:[0,0],3:[0,0],4:[0,0],5:[0,0],6:[0,0],7:[0,0],8:[0,0],9:[0,0],10:[0,0],11:[0,0],12:[0,0]}

				# Initialize Total monthly reve
				TotalMonthlyRev = ['x',0]

				# Initialize these variables for each location to begin adding them up.
				HighMonthlySalePrice = ['x',0]
				HighSale = 0
				LowSale = 100000000
				TotalRev = 0
				TotalMil = 0
				TotalAge = 0
				AvgAge = 0
				AvgPrice = 0
				AvgMil = 0
				SoldAssets = 0
				ValidSoldAssets = 0

				# Add "AND Location ='%s'" to sql statement to make the data rows specific the location being dealt with
				str1 = ("AND Location ='%s'" % keys)
				sql1 = sql + str1

				# Make a copy of the original dataframe
				df1 = df

				# Iterate through all the rows in the dataframe
				for index, rows in df1.sort_values('Location').iterrows():
					# Only care about the rows that have the current location name
					if keys == rows['Location']:
						# Increment the number of sold assets
						SoldAssets += 1
						# This nested try/except first tries to add the saleprice, if it doesn't have a sale price then we skip the row.
						try:
							TotalRev = TotalRev + int(rows['SalesPrice'])
							# This nested try/except then tries to add the hours/mileage/reeferhours to the Total Mileage variable.
							try:
								TotalMil = TotalMil + int(rows['Hours'])
							except:
								try:
									TotalMil = TotalMil + int(rows['Mileage'])
								except:
									try:
										TotalMil = TotalMil + int(rows['ReeferHours'])
									except:
										# If there is no 'hours/mileage/reeferhours' column heading, set the Total Mileage var to 0
										TotalMil = 0
							# Increment the total age as the Saledate year subtract the manufacturing
							TotalAge += int(str(rows['SaleDate'])[0:4]) - int(rows['Year'])
							ValidSoldAssets += 1
						except:
							continue
						# These 7 lines below just update the highest sale price and lowest sale price, as well as the months they occur in, respectively
						Months[int(str(rows['SaleDate'])[5:7])][0] += int(rows['SalesPrice']) # Accumulate TotalMonthlyRev
						if int(rows['SalesPrice']) > Months[int(str(rows['SaleDate'])[5:7])][1]:
							Months[int(str(rows['SaleDate'])[5:7])][1] = int(rows['SalesPrice']) # Calculate HighestSale per month
						if int(rows['SalesPrice']) > HighSale:
							HighSale = int(rows['SalesPrice'])
						if int(rows['SalesPrice']) < LowSale:
							LowSale = int(rows['SalesPrice'])

				# If the location name is 'None', skip it
				if str(keys) == 'None':
					continue

				# This section stores all the data for each location
				AvgAge = round(TotalAge/SoldAssets,2)
				AvgPrice = round(TotalRev/SoldAssets,2)
				AvgMil = round(TotalMil/SoldAssets,2)
				Locs[keys]['TotalRev'] = TotalRev
				Locs[keys]['HighSale'] = HighSale
				Locs[keys]['LowSale'] = LowSale
				Locs[keys]['AvgPrice'] = AvgPrice
				Locs[keys]['AvgAge'] = AvgAge
				Locs[keys]['AvgMil'] = AvgMil
				Locs[keys]['SoldAssets'] = SoldAssets

				# This section tries to check if the location is a key in the Locations GPSdict opened earlier.
				# It usually belongs to the GPSdict, but if not, it computes it using the geocode library.
				newkeys = keys.lower()
				if any(char.isdigit() for char in keys.lower()):
					newkeys = keys.lower()[:-6]
				if newkeys in GPSdict:
					Locs[keys]['lat'] = GPSdict[newkeys][0]
					Locs[keys]['long'] = GPSdict[newkeys][1]
					print(newkeys + " in dict")
				else:
					print(newkeys + " Not in dict")
					try:
						location = gn.geocode(keys)
						lat = location.raw['lat']
						long = location.raw['lng']
						Locs[keys]['lat'] = lat
						Locs[keys]['long'] = long
					except:
						Locs[keys]['lat'] = 0
						Locs[keys]['long'] = 0

				# This section deals with the most revenue month and highest sale month. However, most revenue month isn't used on the interface.
				for month in Months:
					if Months[month][0] > TotalMonthlyRev[1]:
						TotalMonthlyRev[1] = Months[month][0]
						TotalMonthlyRev[0] = month
					if Months[month][1] > HighMonthlySalePrice[1]:
						HighMonthlySalePrice[1] = Months[month][1]
						HighMonthlySalePrice[0] = month
				Locs[keys]['MostRevMonth'] = TotalMonthlyRev[0]
				Locs[keys]['HighSaleMonth'] = HighMonthlySalePrice[0]

			# This section computes the average for each metric across all locations.
			TotalTotalRev = 0
			TotalAvgPrice = 0
			TotalAvgMil = 0
			TotalAvgAge = 0
			TotalHighSale = 0
			TotalLowSale = 0
			TotalSoldAssets = 0
			TotalHighSaleMonth= 0
			count = 0
			mileagecount = 0 # This is used to count data rows that actually have a mileage value.
			LocsAvg = {}
			for locs in Locs:
				TotalTotalRev = TotalTotalRev + Locs[locs]['TotalRev']
				TotalAvgPrice = TotalAvgPrice + Locs[locs]['AvgPrice']
				TotalAvgMil = TotalAvgMil + Locs[locs]['AvgMil']
				TotalAvgAge = TotalAvgAge + Locs[locs]['AvgAge']
				TotalHighSale = TotalHighSale + Locs[locs]['HighSale']
				TotalLowSale = TotalLowSale + Locs[locs]['LowSale']
				TotalSoldAssets = TotalSoldAssets + Locs[locs]['SoldAssets']
				try:
					TotalHighSaleMonth = TotalHighSaleMonth + Locs[locs]['HighSaleMonth']
				except:
					TotalHighSaleMonth = 0
				count +=  1
				if Locs[locs]['AvgMil'] > 0: # If AvgMil is a valid number, greater than 0, increment the mileage count, which tracks the total number of assets with valid milage/hours/reeferhours
					mileagecount += 1
			LocsAvg['TotalRev'] = TotalTotalRev/count
			LocsAvg['AvgPrice'] = TotalAvgPrice/count
			try: # Try dividing by the mileage count. It won't work if the number is 0 or Null valued, so just set to 0 in that case
				LocsAvg['AvgMil'] = TotalAvgMil/mileagecount
			except:
				LocsAvg['AvgMil'] = 0
			LocsAvg['AvgAge'] = TotalAvgAge/count
			LocsAvg['HighSale'] = TotalHighSale/count
			LocsAvg['LowSale'] = TotalLowSale/count
			LocsAvg['SoldAssets'] = TotalSoldAssets/count
			LocsAvg['HighSaleMonth'] = TotalHighSaleMonth/count
			temp = LocsAvg['HighSale']
			MonthName = MList[round(LocsAvg['HighSaleMonth'],0)]
			LocsAvg['HighSale'] = "%s, %s" % (round(LocsAvg['HighSale'],2), MonthName) # Reformat the Avg highsale as the avg high sale, and the avg month of occurence

			# This statement generates an html formatted string to be inserted to as the top table row in index.html
			TableDataAvg = '<th scope="col">0</th><th scope="col">Average</th><th scope="col">%s</th><th scope="col">%s</th><th scope="col">%s</th><th scope="col">%s</th><th scope="col">%s</th><th scope="col">%s</th><th scope="col">%s</th>' % (round(LocsAvg['TotalRev'],2),round(LocsAvg['AvgPrice'],2),round(LocsAvg['AvgMil'],2),round(LocsAvg['AvgAge'],2),LocsAvg['HighSale'],round(LocsAvg['LowSale'],2),round(LocsAvg['SoldAssets'],2))

			# Call the ranking function to output a list of locations, ordered by AvgPrice by default, where each location has attached to it a dictionary of all the metrics
			RankedLocs = RankMap(Locs,'AvgPrice',True)
			print(RankedLocs)

			count = 0 # Count to keep track of the table rows
			TableData = "" # String that will be used to hold the HTML code that forms the body of the table with all the rows

			# This for loop goes through each element in the list, RankedLocs, where each element is a key and a dictionary, with the key being a location.
			for keys in RankedLocs:
				count += 1
				strdict = {}
				itemlist = ["TotalRev", "AvgPrice", "AvgMil", "AvgAge", "HighSale", "LowSale", "SoldAssets"]
				for items in keys[1]:
					if items not in itemlist: # Item list controls what columns we care about of all the metrics attached to each location
						continue
					# THe below pct calculations are for generating the +/- percentages of each metric according to the Average across all locations.
					try:
						if items is "HighSale": # Since the value at highsale is a string, containing the highest sale price and the corresponding month,
							pct = keys[1][items]/temp # we handle this value differently than the rest.
						else:
							pct = keys[1][items]/LocsAvg[items]
					except:
						pct = 1
					str1 = ""
					MonthName = MList[keys[1]['HighSaleMonth']]
					if pct < 1: # A pct less than one will be styled as below in red, with the calculation made as round(100*(1-pct),2)
						if items == 'HighSale':
							str1 = '<td>%s, %s<br><p style="color:red">-%s &#37</p></td>' % (keys[1][items],MonthName, round(100*(1-pct),2))
						else:
							str1 = '<td>%s<br> <p style="color:red">-%s &#37</p></td>' % (keys[1][items], round(100*(1-pct),2))
					else: # A pct greater than one will be styled as below in green, with the calculation made as round(100*(pct-1),2)
						if items == 'HighSale':
							str1 = '<td>%s, %s<br> <p style="color:green">+%s &#37</p></td>' % (keys[1][items],MonthName, round(100*(pct-1),2))
						else:
							str1 = '<td>%s<br> <p style="color:green">+%s &#37</p></td>' % (keys[1][items], round(100*(pct-1),2))
					strdict[items] = str1
				# Set the first row as active, the rest are inactive
				if count == 1:
					tablerow = '<tr class="clickable-row active"><th scope="row">%s</th><td>%s</td>%s%s%s%s%s%s%s</tr>' % (count,RankedLocs[count-1][0],strdict['TotalRev'], 	strdict['AvgPrice'],strdict['AvgMil'],strdict['AvgAge'],strdict['HighSale'],strdict['LowSale'],strdict['SoldAssets'])
				else:
					tablerow = '<tr class="clickable-row"><th scope="row">%s</th><td>%s</td>%s%s%s%s%s%s%s</tr>' % (count,RankedLocs[count-1][0],strdict['TotalRev'], strdict['AvgPrice'],strdict['AvgMil'],strdict['AvgAge'],strdict['HighSale'],strdict['LowSale'],strdict['SoldAssets'])
				TableData = TableData + tablerow # Keep appending the HTML style rows to the TableData string.

			# Save the transposed dataframe to MapData.csv for reference in plotly.js in index.html
			DFrame1 = pd.DataFrame(Locs).T
			DFrame1.to_csv("dashboard/static/dashboard/csv/MapData.csv")


			# Save the Locs dictionary to Locs.txt to give ability to pull this data from index.html
			text_file = open("dashboard/static/dashboard/csv/Locs.txt", "w")
			text_file.write("%s" % str(Locs))
			text_file.close()

			# Save the RankedLocs list of dicts to RankedLocs.txt to give ability to pull this data from index.html
			text_file = open("dashboard/static/dashboard/csv/RankedLocs.txt", "w")
			text_file.write("%s" % str(RankedLocs))
			text_file.close()


		# Added by Kyle
		#print(sql)
		Data = pd.read_sql(sql,cnxn)

		# print(Data.head())
		#print(Data.columns)

		# Add yearmonth column as the label of the box and whisker plot
		# yearmonth = Data.SaleDate.dt.strftime('%Y/%m') # Can later add '%Y/%m/%d' to do daily boxes, or '%Y' for Yearly...
		# yearmonth = Data.SaleDate.dt.strftime('%Y/%m/%d')
		yearmonth = Data.SaleDate.dt.strftime('%Y')
		# Add yearmonth as a column onto data
		Data["YearMonth"] = yearmonth

		# print(Data.head())

		# Data.to_csv("dashboard/static/dashboard/csv/AllData.csv", columns=["SalesPrice", "SaleDate", "Location", "YearMonth"])
		Data.to_csv("dashboard/static/dashboard/csv/AllData.csv")

		# For each unique value in yearmonth, append all of the datapoints with that yearmonth as a column in a csv

		# write_hist_data(Data, 2012)
		write_hist_data(Data)

		# Generate an HTML string that says how many assets are included and filtered out
		FilteredAssets = "<b>Based on " + str(DataRowsA) + " of " + str(DataRowsB) + " assets.</b><br><br>Unselecting 'Mileage/hours' may help to include more assets.<br> This is due to the fact that a large portion of the data does not contain valid mileage/hours data."

		# JSON data dump

		# Kyle Edit to make the table optional
		if UseTable == 'true':
			data_details = {'FilteredAssets':FilteredAssets,'Years':'Yup','0' : TableData,'1': TableDataAvg, '2': str(Locs),'4':str(RankedLocs)}
		else:
			data_details = {'FilteredAssets':FilteredAssets,'Years':'Yup'}

		return JsonResponse(data_details)

	return render(request)


# Update the histogram and highlight the specified year
def update_hist_data(request):

	if request.method == "GET":
		highlight_year = request.GET['highlight_year']
		HistDataLocations = request.GET['HistDataLocations']
		bin_size = request.GET['HistDataBinSize']
		data = pd.read_csv("dashboard/static/dashboard/csv/AllData.csv", parse_dates=["SaleDate"])
		data = data.drop(columns=["Unnamed: 0"])
		print(highlight_year)
		if(highlight_year == "None"):
			highlight_year = None
		else:
			highlight_year = int(highlight_year)
		if(HistDataLocations == "None"):
			HistDataLocations = None

		strf = ''
		if(bin_size == "1"):
			strf = '%Y/%m/%d'
		elif(bin_size == "7"):
			strf = '%Y W%W'
		elif(bin_size == "28"):
			strf = '%Y/%m'
		elif(bin_size == '365'):
			strf = '%Y'

		yearmonth = data.SaleDate.dt.strftime(strf)
		# Add yearmonth as a column onto data
		data["YearMonth"] = yearmonth
		# print(data.head())

		write_hist_data(data, highlight_year, HistDataLocations)

		# Delay to allow the csv to load
		# import time
		# time.sleep(5)
		# JSON Data dump
		data_details = {'0':0} #???
		return JsonResponse(data_details)
	return render(request)

# def update_hist_location_data(request):

# 	def write_hist_location_data(Data, HistDataLocations=None):

# 		Data.to_csv("dashboard/static/dashboard/csv/HistData.csv", columns=["SaleDate","SalesPrice"])
# 		# Make a second csv with just a single years worth of data, to turn a different colour upon a change in the map slider
# 		if(type(highlight_year) != type(None)):
# 			single_year = Data[Data['SaleDate'].dt.year==highlight_year]
# 			single_year.to_csv("dashboard/static/dashboard/csv/HistData_single_year.csv", columns=["SaleDate","SalesPrice"])
# 		else: # If no year is supplied highlight all the data
# 			Data.to_csv("dashboard/static/dashboard/csv/HistData_single_year.csv", columns=["SaleDate","SalesPrice"])

# 	if request.method == "GET":
# 		HistDataLocations = request.GET['HistDataLocations']
# 		data = pd.read_csv("dashboard/static/dashboard/csv/AllData.csv", parse_dates=["SaleDate"])
# 		# print(highlight_year)
# 		if(HistDataLocations == "None"):
# 			HistDataLocations = None

# 		write_hist_location_data(data, HistDataLocations)

# 		# Delay to allow the csv to load
# 		# import time
# 		# time.sleep(5)
# 		# JSON Data dump
# 		data_details = {'0':0} #???
# 		return JsonResponse(data_details)
# 	return render(request)


# Update table data upon changing the sorting method in the dropdown menu list in the table data panel
def updatetabledata(request):

	# Rank Function for ordering the locations, stored in RankedLocs, by the selected TableDataRankBy value
	def RankMap(dictt, string, Reverse):
		Ranked = sorted(
			dictt.items(), key=lambda x: x[1][string], reverse=Reverse)
		print(Ranked)
		return Ranked

	if request.method == 'GET':
		TableDataRankBy = request.GET['TableDataRankBy']

		# Get current Locs dictionary from Locs.txt
		text_file = open("dashboard/static/dashboard/csv/Locs.txt", "r")
		Arr = text_file.readlines()
		Locs = ast.literal_eval(Arr[0])
		text_file.close()

		# Update RankedLocs list to be ranked by selected TableDataRankBy value
		RankedLocs = RankMap(Locs, TableDataRankBy, True)

		# Have to compute the Avg Location data again in order to compute percentages
		# This process is exactly the same as the process outlined in the getData function above.

		# Initialize counting variables
		TotalTotalRev = 0
		TotalAvgPrice = 0
		TotalAvgMil = 0
		TotalAvgAge = 0
		TotalHighSale = 0
		TotalLowSale = 0
		TotalSoldAssets = 0
		count = 0
		mileagecount = 0

		# Loop through all locations
		LocsAvg = {"AvgTotalRev": 0, "AvgAvgPrice": 0, "AvgAvgMil": 0,
				   "AvgAvgAge": 0, "AvgHighSale": 0, "AvgLowSale": 0, "AvgSoldAssets": 0}
		for locs in Locs:
			TotalTotalRev = TotalTotalRev + Locs[locs]['TotalRev']
			TotalAvgPrice = TotalAvgPrice + Locs[locs]['AvgPrice']
			TotalAvgMil = TotalAvgMil + Locs[locs]['AvgMil']
			TotalAvgAge = TotalAvgAge + Locs[locs]['AvgAge']
			TotalHighSale = TotalHighSale + Locs[locs]['HighSale']
			TotalLowSale = TotalLowSale + Locs[locs]['LowSale']
			TotalSoldAssets = TotalSoldAssets + Locs[locs]['SoldAssets']
			count += 1
			if Locs[locs]['AvgMil'] > 0:  # Increment mileagecount for valid mileage values
				mileagecount += 1
		LocsAvg['TotalRev'] = TotalTotalRev/count
		LocsAvg['AvgPrice'] = TotalAvgPrice/count
		try:
			# Try computing the average if the mileagecount is a valid value.
			LocsAvg['AvgMil'] = TotalAvgMil/mileagecount
		except:
			LocsAvg['AvgMil'] = 0
		LocsAvg['AvgAge'] = TotalAvgAge/count
		LocsAvg['HighSale'] = TotalHighSale/count
		LocsAvg['LowSale'] = TotalLowSale/count
		LocsAvg['SoldAssets'] = TotalSoldAssets/count
		count = 0
		TableData = ""

		# For each metric attached to each location, compute percentage above or below avg location metrics.
		for keys in RankedLocs:
			count += 1
			strdict = {}
			print(keys[1])
			itemlist = ["TotalRev", "AvgPrice", "AvgMil",
						"AvgAge", "HighSale", "LowSale", "SoldAssets"]
			for items in keys[1]:
				if items not in itemlist:
					continue
				print(items)
				try:
					if items is "HighSale":
						pct = keys[1][items]/temp
					else:
						pct = keys[1][items]/LocsAvg[items]
				except:
					pct = 1
				#pct = keys[1][items]/LocsAvg[items]
				str1 = ""
				MonthName = MList[keys[1]['HighSaleMonth']]
				if pct < 1:
					if items == 'HighSale':
						str1 = '<td>%s, %s<br><p style="color:red">-%s &#37</p></td>' % (
							keys[1][items], MonthName, round(100*(1-pct), 2))
					else:
						str1 = '<td>%s<br> <p style="color:red">-%s &#37</p></td>' % (
							keys[1][items], round(100*(1-pct), 2))
				else:
					if items == 'HighSale':
						str1 = '<td>%s, %s<br> <p style="color:green">+%s &#37</p></td>' % (
							keys[1][items], MonthName, round(100*(pct-1), 2))
					else:
						str1 = '<td>%s<br> <p style="color:green">+%s &#37</p></td>' % (
							keys[1][items], round(100*(pct-1), 2))
				strdict[items] = str1
			if count == 1:
				tablerow = '<tr class="clickable-row active"><th scope="row">%s</th><td>%s</td>%s%s%s%s%s%s%s</tr>' % (
					count, RankedLocs[count-1][0], strdict['TotalRev'], strdict['AvgPrice'], strdict['AvgMil'], strdict['AvgAge'], strdict['HighSale'], strdict['LowSale'], strdict['SoldAssets'])
			else:
				tablerow = '<tr class="clickable-row"><th scope="row">%s</th><td>%s</td>%s%s%s%s%s%s%s</tr>' % (
					count, RankedLocs[count-1][0], strdict['TotalRev'], strdict['AvgPrice'], strdict['AvgMil'], strdict['AvgAge'], strdict['HighSale'], strdict['LowSale'], strdict['SoldAssets'])
			TableData = TableData + tablerow

		# JSON Data dump
		data_details = {'0': TableData}

		# Write updated RankedLocs list to RankedLocs.txt
		text_file = open("dashboard/static/dashboard/csv/RankedLocs.txt", "w")
		text_file.write("%s" % str(RankedLocs))
		text_file.close()

		return JsonResponse(data_details)

	return render(request)

# Load categories into category dropdown list upon page loading


def populatedropdowns(request):
	if request.method == 'GET':
		"""
		# Access database table of categories
		#cnxn = pyodbc.connect('DSN=MYMSSQL;UID=sa;PWD=Q1w2e3r4t5y6u7i8o9p0')
		sql = "SELECT * FROM QMIND.dbo.DBDutyType where ParentDutyTypeID is null"
		print(sql)
		Data = pd.read_sql(sql,cnxn)

		# Create subset of data of category display names
		dfDuty = Data[['DisplayName']].drop_duplicates('DisplayName').sort_values('DisplayName')['DisplayName']
		print(dfDuty)

		# Add all category display names to an HTML style string for a dropdown list of items
		DropDownListCat = "<option value="">Select Category</option>"
		for item in dfDuty: # Don't include any EMG categories, or Aircrafts
				if "EMG" in str(item):
						continue
				if "Air" in str(item):
						continue
				DropDownItem = '<option value="%s">%s</option>' % (item, item)
				DropDownListCat = DropDownListCat + DropDownItem

		"""

		# ADDED FOR QMIND TEAM
		DropDownListCat = "<option value="">Select Category</option>"
		DropDownItem = '<option value="Tractors">Tractors</option>'
		DropDownListCat = DropDownListCat + DropDownItem
		# ADDED FOR QMIND TEAM

		data_details = {'0': DropDownListCat}

		return JsonResponse(data_details)
	return render(request)

# Load dropdown list of dutytypes upon selecting a category


def populatedropdownsCat(request):
	if request.method == 'GET':

		# Get selected category
		Category = request.GET['Category']

		# Access database table of categories
		#cnxn = pyodbc.connect('DSN=MYMSSQL;UID=sa;PWD=Q1w2e3r4t5y6u7i8o9p0')
		#cnxn = pyodbc.connect('Driver=ODBC Driver 17 for SQL Server;Server=localhost;Database=DCMM;Port: 1433;UID=sa;PWD=Q1w2e3r4t5y6u7i8o9p0')

		"""
		sql = "SELECT * FROM QMIND.dbo.DBDutyType where ParentDutyTypeID is null"
		Data1 = pd.read_sql(sql,cnxn)
		print(Data1)

		# Get row in dataframe where displayname == selected category
		df = Data1.loc[Data1['DisplayName'] == Category]

		# Get ID of selected category, since displayname can't be used to access category table in db
		CatID = df['DutyTypeID'].iloc[0]

		# Create SQL query to get selected categories table data
		sql1 = "select * from QMIND.dbo.DBDutyType where ParentDutyTypeID='%s'" %CatID
		Data1 = pd.read_sql(sql1,cnxn)
		print(Data1)

		# Create subset of dataframe of DutyType descriptions
		dfDuty = Data1[['DutyTypeDesc']].sort_values('DutyTypeDesc')['DutyTypeDesc']
		print(dfDuty)

		# Use this new subset of data to populate the dropdown list of dutytypes
		DropDownListDuty = "<option value="">Select Dutytype</option>"
		for item in dfDuty:
			DropDownItem = '<option value="%s">%s</option>' % (item, item)
			DropDownListDuty = DropDownListDuty + DropDownItem
		"""

		# ADDED FOR QMIND TEAM

		# Kyle Change
		# sql = "SELECT * FROM QMIND.dbo.Tractors"
		sql = "SELECT DutyType FROM QMIND.dbo.Tractors"
		Data1 = pd.read_sql(sql, cnxn)
		print(list(set(Data1.DutyType.values)))

		DropDownListDuty = "<option value="">Select Dutytype</option>"
		for item in list(set(Data1.DutyType.values)):
			DropDownItem = '<option value="%s">%s</option>' % (item, item)
			DropDownListDuty = DropDownListDuty + DropDownItem

		data_details = {'0': DropDownListDuty}

		return JsonResponse(data_details)
	return render(request)

# Load dropdown list of all makes, models, and years upon selecting a dutytype


def populatedropdownsDuty(request):
	if request.method == 'GET':

		# Get selected category and dutytype
		Dutytype = request.GET['Dutytype']
		Category = request.GET['Category']

		"""
		#cnxn = pyodbc.connect('DSN=MYMSSQL;UID=sa;PWD=Q1w2e3r4t5y6u7i8o9p0')

		# Using category display name, get categories ID name to access database
		sql1 = "SELECT * FROM QMIND.dbo.DBDutyType where ParentDutyTypeID is null"
		Data1 = pd.read_sql(sql1,cnxn)
		print(Data1)
		df = Data1.loc[Data1['DisplayName'] == Category]
		Category = df['DutyTypeDesc'].iloc[0]

		"""
		# Get all data under specified dutytype and category

		# Kyle change
		# sql = "SELECT * FROM QMIND.dbo.[%s] where DUTYTYPE = '%s'" %(Category, Dutytype)
		sql = "SELECT Make, Model, Year, DutyType FROM QMIND.dbo.[%s] where DUTYTYPE = '%s'" % (
			Category, Dutytype)

		print(sql)
		Data = pd.read_sql(sql, cnxn)

		# Count total number of each unique Make, Model, and Year, that appear in the data. These values are attached in the respective dropdown list values to show number of data rows for each selectable value
		dfMakecount = Data.groupby('Make').count()['DutyType']
		dfModelcount = Data.groupby('Model').count()['DutyType']
		dfYearcount = Data.groupby('Year').count()['DutyType']

		# Get sorted lists of unique Makes, Models, and years, respectively.
		dfMake = Data[['Make']].drop_duplicates(
			'Make').sort_values('Make')['Make']
		print(dfMake)
		dfModel = Data[['Model']].drop_duplicates(
			'Model').sort_values('Model')['Model']
		print(dfModel)
		dfYear = Data[['Year']].drop_duplicates(
			'Year').sort_values('Year')['Year']
		print(dfYear)

		# Populate Make HTML dropdown string
		DropDownListMake = "<option value="">Select Make</option>"
		for item in dfMake:
			if item is None:
				continue
			DropDownItem = '<option value="%s">%s (%s)</option>' % (
				item, item, dfMakecount[item])
			DropDownListMake = DropDownListMake + DropDownItem

		# Populate Model HTML dropdown string
		DropDownListModel = "<option value="">Select Model</option>"
		for item in dfModel:
			if item is None:
				continue
			DropDownItem = '<option value="%s">%s (%s)</option>' % (
				item, item, dfModelcount[item])
			DropDownListModel = DropDownListModel + DropDownItem

		# Populate Year HTML dropdown string
		DropDownListYear = "<option value="">Select Year</option>"
		for item in dfYear:
			if item is None:
				continue
			DropDownItem = '<option value="%s">%s (%s)</option>' % (
				item, item, dfYearcount[item])
			DropDownListYear = DropDownListYear + DropDownItem

		data_details = {'0': DropDownListMake,
						'1': DropDownListModel, '2': DropDownListYear}

		return JsonResponse(data_details)
	return render(request)

# Load dropdown list of all models and years upon selecting a make


def populatedropdownsMake(request):
	if request.method == 'GET':

		# Get selected category, dutytype, and make
		Dutytype = request.GET['Dutytype']
		Category = request.GET['Category']
		Make = request.GET['Make']
		#cnxn = pyodbc.connect('DSN=MYMSSQL;UID=sa;PWD=Q1w2e3r4t5y6u7i8o9p0')

		"""
		# Using category display name, get categories ID name to access database
		sql1 = "SELECT * FROM QMIND.dbo.DBDutyType where ParentDutyTypeID is null"
		Data1 = pd.read_sql(sql1,cnxn)
		print(Data1)
		df = Data1.loc[Data1['DisplayName'] == Category]
		Category = df['DutyTypeDesc'].iloc[0]
		"""
		# Get all data under specified dutytype and category
		sql = "SELECT * FROM QMIND.dbo.%s where DUTYTYPE = '%s' and MAKE = '%s'" % (
			Category, Dutytype, Make)
		print(sql)
		Data = pd.read_sql(sql, cnxn)

		# Count total number of each unique Model and Year, that appear in the data
		dfModelcount = Data.groupby('Model').count()['DutyType']
		dfYearcount = Data.groupby('Year').count()['DutyType']

		# Get sorted lists of unique models, and years, respectively.
		dfModel = Data[['Model']].drop_duplicates(
			'Model').sort_values('Model')['Model']
		print(dfModel)
		dfYear = Data[['Year']].drop_duplicates(
			'Year').sort_values('Year')['Year']
		print(dfYear)

		# Populate Model HTML dropdown string
		DropDownListModel = "<option value="">Select Model</option>"
		for item in dfModel:
			if item is None:
				continue
			DropDownItem = '<option value="%s">%s (%s)</option>' % (
				item, item, dfModelcount[item])
			DropDownListModel = DropDownListModel + DropDownItem

		# Populate Year HTML dropdown string
		DropDownListYear = "<option value="">Select Year</option>"
		for item in dfYear:
			if item is None:
				continue
			DropDownItem = '<option value="%s">%s (%s)</option>' % (
				item, item, dfYearcount[item])
			DropDownListYear = DropDownListYear + DropDownItem

		data_details = {'0': DropDownListModel, '1': DropDownListYear}

		return JsonResponse(data_details)
	return render(request)

# Load dropdown list of all years upon selecting a model


def populatedropdownsModel(request):
	if request.method == 'GET':

		# Get selected category, dutytype, make, and year
		Dutytype = request.GET['Dutytype']
		Category = request.GET['Category']
		Make = request.GET['Make']
		Model = request.GET['Model']

		"""
		# Using category display name, get categories ID name to access database
		#cnxn = pyodbc.connect('DSN=MYMSSQL;UID=sa;PWD=britelite')
		sql1 = "SELECT * FROM QMIND.dbo.DBDutyType where ParentDutyTypeID is null"
		Data1 = pd.read_sql(sql1,cnxn)
		print(Data1)
		df = Data1.loc[Data1['DisplayName'] == Category]
		Category = df['DutyTypeDesc'].iloc[0]
		"""

		# Handle user selection possibilities to create the proper SQL query
		if Make == '' and Dutytype == '':
			sql = "SELECT * FROM QMIND.dbo.%s where MODEL = '%s'" % (
				Category, Model)
		if Make == '' and Dutytype != '':
			sql = "SELECT * FROM QMIND.dbo.%s where DUTYTYPE = '%s' and MODEL = '%s'" % (
				Category, Dutytype, Model)
		if Make != '' and Dutytype == '':
			sql = "SELECT * FROM QMIND.dbo.%s where MAKE = '%s' and MODEL = '%s'" % (
				Category, Make, Model)
		if Make != '' and Dutytype != '':
			sql = "SELECT * FROM QMIND.dbo.%s where DUTYTYPE = '%s' and MODEL = '%s' and MAKE = '%s'" % (
				Category, Dutytype, Model, Make)
		print(sql)
		Data = pd.read_sql(sql, cnxn)

		# Count total number of each unique Year that appear in the data
		dfYearcount = Data.groupby('Year').count()['DutyType']

		# Get sorted lists of unique models, and years, respectively.
		dfYear = Data[['Year']].drop_duplicates(
			'Year').sort_values('Year')['Year']

		# Populate Year HTML dropdown string
		DropDownListYear = "<option value="">Select Year</option>"
		for item in dfYear:
			if item is None:
				continue
			DropDownItem = '<option value="%s">%s (%s)</option>' % (
				item, item, dfYearcount[item])
			DropDownListYear = DropDownListYear + DropDownItem

		data_details = {'0': DropDownListYear}

		return JsonResponse(data_details)
	return render(request)


# Load dropdown list of all locations for use in the histogram
def populate_dropdowns_location(request):
	if request.method == 'GET':

		# Get selected category, dutytype, make, and year
		Dutytype = request.GET['Dutytype']
		Category = request.GET['Category']
		Make = request.GET['Make']
		Model = request.GET['Model']

		"""
		# Using category display name, get categories ID name to access database
		#cnxn = pyodbc.connect('DSN=MYMSSQL;UID=sa;PWD=britelite')
		sql1 = "SELECT * FROM QMIND.dbo.DBDutyType where ParentDutyTypeID is null"
		Data1 = pd.read_sql(sql1,cnxn)
		print(Data1)
		df = Data1.loc[Data1['DisplayName'] == Category]
		Category = df['DutyTypeDesc'].iloc[0]
		"""

		# Handle user selection possibilities to create the proper SQL query
		if Make == '' and Dutytype == '':
			sql = "SELECT * FROM QMIND.dbo.%s where MODEL = '%s'" % (
				Category, Model)
		if Make == '' and Dutytype != '':
			sql = "SELECT * FROM QMIND.dbo.%s where DUTYTYPE = '%s' and MODEL = '%s'" % (
				Category, Dutytype, Model)
		if Make != '' and Dutytype == '':
			sql = "SELECT * FROM QMIND.dbo.%s where MAKE = '%s' and MODEL = '%s'" % (
				Category, Make, Model)
		if Make != '' and Dutytype != '':
			sql = "SELECT * FROM QMIND.dbo.%s where DUTYTYPE = '%s' and MODEL = '%s' and MAKE = '%s'" % (
				Category, Dutytype, Model, Make)
		print(sql)
		Data = pd.read_sql(sql, cnxn)

		# Count total number of each unique Year that appear in the data
		dfYearcount = Data.groupby('Year').count()['DutyType']

		# Get sorted lists of unique models, and years, respectively.
		dfYear = Data[['Year']].drop_duplicates(
			'Year').sort_values('Year')['Year']

		# Populate Year HTML dropdown string
		DropDownListYear = "<option value="">Select Year</option>"
		for item in dfYear:
			if item is None:
				continue
			DropDownItem = '<option value="%s">%s (%s)</option>' % (
				item, item, dfYearcount[item])
			DropDownListYear = DropDownListYear + DropDownItem

		data_details = {'0': DropDownListYear}

		return JsonResponse(data_details)
	return render(request)

# get data needed for leaflet map slider,


def getSliderData(request):
	if request.method == 'GET':
		df = pd.read_csv('dashboard/static/dashboard/csv/AllData.csv')
		datesStr = df['SaleDate'].astype(str)
		yearsStr = datesStr.str.slice(0, 4).tolist()
		years = sorted(list(set(yearsStr)))

		DropDownListYear = "<option value="">Select Year</option>"
		for item in years:
			if item is None:
				continue
			DropDownItem = '<option value="%s">%s</option>' % (item, item)
			DropDownListYear = DropDownListYear + DropDownItem

		json = {'location': df['Location'].tolist(), 'saledate': df['SaleDate'].tolist(),
				'years': years, 'years_html': DropDownListYear}
		return JsonResponse(json)
	return render(request)


# def populatedropdownsMapYear(request):
#     if request.method == 'GET':
#         df = pd.read_csv('dashboard/static/dashboard/csv/AllData.csv')
#         years = sorted(
#             list(set(df['SaleDate'].astype(str).slice(0, 4).tolist())))
#
#         DropDownListYear = "<option value="">Select Year</option>"
#         for item in years:
#             if item is None:
#                 continue
#             DropDownItem = '<option value="%s">%s</option>' % (item, item)
#             DropDownListYear = DropDownListYear + DropDownItem
#         json = {'html': DropDownListYear}
#         return JsonResponse(json)
#     return render(request)
