from django.shortcuts import render, redirect
import pandas as pd
import numpy as np
import json

def map(request):
    df = pd.read_excel("map/static/map/tractor_data.xlsx")
    locations = np.array(df['Location'].dropna().tolist())      #getting locations into np array with no NaN values

    otherData = {'Make': df['Make'].dropna().tolist(), 'Model': df['Model'].dropna().tolist(), 'Location': df['Location'].dropna().tolist(),
                    'SaleDate': df['SaleDate'].dropna().tolist(), 'Salesprice': df['Salesprice'].dropna().tolist(), 'Adjusted_Salesprice': df['Adjusted_Salesprice'].dropna().tolist()}

    otherData['SaleDate'] = [str(i) for i in otherData['SaleDate']]

    #if state code is legal, add it to its respective count in countDict
    countDict = {}
    legalStates = ['AL','AK','AZ','AR','CA','CO','CT','DE','DC','FL',
                   'GA','HI','ID','IL','IN','IA','KS','KY','LA','ME',
                   'MD','MA','MI','MN','MS','MO','MT','NE','NV','NH',
                   'NJ','NM','NY','NC','ND','OH','OK','OR','PA','RI',
                   'SC','SD','TN','TX','UT','VT','VA','WA','WV','WI','WY']
    for i in range(len(locations)):
        if locations[i][-2:] in legalStates:
            if locations[i][-2:] in countDict:
                countDict[locations[i][-2:]] += 1
            else:
                countDict[locations[i][-2:]] = 1

    # loading geoJSON data of us states
    with open("map/static/map/us-states.json") as geoJSON:
        us_states = json.load(geoJSON)
    mapData = us_states['features']     #pointer to the features of each state

    # adding a saleCount property to each state, with the value being the state's entry in countDict
    for i in range(len(mapData)):
        try:
            mapData[i]['properties']['saleCount'] = countDict[mapData[i]['id']]
        except KeyError:
            continue

    return render(request, 'map/index.html', context={'us_states' : json.dumps(us_states), 'other_data': json.dumps(otherData)})
