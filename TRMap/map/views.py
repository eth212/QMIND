from django.shortcuts import render, redirect
import pandas as pd
import numpy as np
import json
import datetime


def map(request):
    df = pd.read_excel("map/static/tractor_data.xlsx")
    noNaNs = df.fillna(0)

    # getting locations into np array with no NaN values
    locations = np.array(df['Location'].dropna().tolist())

    otherData = {'make': noNaNs['Make'].tolist(), 'model': noNaNs['Model'].tolist(), 'location': noNaNs['Location'].tolist(),  # getting other data for maps
                 'saledate': noNaNs['SaleDate'].tolist(), 'salesprice': noNaNs['Salesprice'].tolist(), 'adjusted_salesprice': noNaNs['Adjusted_Salesprice'].tolist()}

    # turning datetimes into strs
    otherData['saledate'] = [str(i) for i in otherData['saledate']]

    # if state code is legal, add it to its respective count in countDict
    countDict = {}
    legalStates = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'DC', 'FL',
                   'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME',
                   'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH',
                   'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI',
                   'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY']
    for i in range(len(locations)):
        if locations[i][-2:] in legalStates:
            if locations[i][-2:] in countDict:
                countDict[locations[i][-2:]] += 1
            else:
                countDict[locations[i][-2:]] = 1

    # loading geoJSON data of us states
    with open("map/static/us-states.json") as geoJSON:
        us_states = json.load(geoJSON)
    mapData = us_states['features']  # pointer to the features of each state

    # adding a saleCount property to each state, with the value being the state's entry in countDict
    for i in range(len(mapData)):
        try:
            mapData[i]['properties']['saleCount'] = countDict[mapData[i]['id']]
        except KeyError:
            continue

    return render(request, 'map/index.html', context={'us_states': json.dumps(us_states), 'other_data': json.dumps(otherData)})


def e(request):
    df = pd.read_excel("map/static/tractor_data.xlsx")
    noNaNs = df.dropna(subset=['SaleDate'])
    # noNaNs['SaleDate'] = pd.to_datetime(noNaNs['SaleDate'])
    noNaNs['SaleDate'] = noNaNs['SaleDate'].apply(lambda x: x.replace(day=1))   #changing all dates to the 1st of the month

    noNaNs['SaleDate'] = noNaNs['SaleDate'].astype(str)             #convert timestamps to string
    noNaNs.sort_values(by=['SaleDate'], inplace=True)               #sort columns by date

    otherData = {'make': noNaNs['Make'].tolist(), 'model': noNaNs['Model'].tolist(), 'location': noNaNs['Location'].tolist(),  # getting other data for maps
                 'saledate': noNaNs['SaleDate'].tolist(), 'salesprice': noNaNs['Salesprice'].tolist(), 'adjusted_salesprice': noNaNs['Adjusted_Salesprice'].tolist()}
    print(otherData['saledate'][:10000])

    df2 = pd.read_csv("map/static/All_Locations_LongLat.csv")
    locationData = {'location': df2['Location'].tolist(
    ), 'longitude': df2['Longitude'].tolist(), 'latitude': df2['Latitude'].tolist()}

    with open("map/static/us-states.json") as geoJSON:
        us_states = json.load(geoJSON)

    return render(request, 'map/e.html', context={'other_data': json.dumps(otherData), 'location_data': json.dumps(locationData), 'us_states': us_states})
