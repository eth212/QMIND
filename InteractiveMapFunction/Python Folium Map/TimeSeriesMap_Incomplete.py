import folium
import pandas as pd
import numpy as np
from folium.plugins import MarkerCluster
from folium.plugins import MeasureControl
from folium.plugins import Search
from folium.plugins import HeatMap
from folium import FeatureGroup, LayerControl, Map, Marker
from folium.plugins import TimestampedGeoJson
from folium.plugins import HeatMapWithTime
from folium import plugins

location_data = pd.read_csv("All_Locations_LongLat.csv")
buffer = pd.read_excel('colab.xlsx')
trac_data = pd.DataFrame(buffer)

df2 = pd.DataFrame(location_data)


trac_data = trac_data.sort_values(by='SaleDate')


str(trac_data.iloc[60][8])[:7]
map = folium.Map(location=[48, -102], zoom_start=4.1)


def retriveCoordinates(location, dfAllLocations):
    for x in range(dfAllLocations.size):
        try:
            if location == dfAllLocations.iloc[x][1]:
                return dfAllLocations.iloc[x][3],dfAllLocations.iloc[x][2]
        except:
            pass
    return 0,0

features = []

def timefunc(date):
    if date == 0.0 or date == '0.0' or date == 0 or date<=1969:
        return 1970;
    return date

timefunc(trac_data.iloc[0][4])

for x in range(0,1000):
        feature = {

                'type': 'Feature',
                'geometry':{
                    'type':'Point',
                    'coordinates':retriveCoordinates(trac_data.iloc[x][9],df2)
                },
                    'properties': {
                    'time':str(trac_data.iloc[x][8])[:10],
                    'style': {'color' : 'red'},
                    'icon': 'circle',
                    'iconstyle': {
                        'fillColor': 'blue',
                        'fillOpacity': 0.8,
                        'stroke': 'true',
                        'radius': 7
                    }
                }

        }
        features.append(feature)


features
TimestampedGeoJson(
        {'type': 'FeatureCollection',
        'features':features}
        , loop_button=True
        , date_options='YYYY'
        , time_slider_drag_update=True
).add_to(map)


map.save('ex6_map.html')
print("Map Done ")


i,j,k=4,5,6
