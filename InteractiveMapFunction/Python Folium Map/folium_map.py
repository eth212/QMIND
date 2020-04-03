import folium
import pandas as pd
import numpy as np
from folium.plugins import MarkerCluster
from folium.plugins import MeasureControl
from folium.plugins import Search
from folium.plugins import HeatMap
from folium import FeatureGroup, LayerControl, Map, Marker
from folium import plugins

location_data = pd.read_csv("All_Locations_LongLat.csv")
buffer = pd.read_excel('colab.xlsx')
trac_data = pd.DataFrame(buffer)

df2 = pd.DataFrame(location_data)

for x in range(df2.size):
    try:
        if df2.iloc[x][3] == 0:
            print(df2.iloc[x][1])

    except:
        pass

map = folium.Map(location=[48, -102], zoom_start=4.1)

feature_group = FeatureGroup(name='Heat Map')

# mini map
map.add_child(plugins.MiniMap(tiles='StamenToner'))
# end mini map


map.add_child(MeasureControl())

marker_cluster = MarkerCluster(name="Product Marker").add_to(map)

# Heat map
heatMapArray = []

# States Border
us_states = 'https://rawcdn.githack.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json'

stategeo = folium.GeoJson(
    us_states,
    name='US State Borders',

    tooltip=folium.GeoJsonTooltip(
        fields=['name'],
        aliases=['State'],
        localize=True

    )

).add_to(map)

statesearch = Search(
    layer=stategeo,
    geom_type='Polygon',
    placeholder='Search for a US State',
    collapsed=False,
    search_label='name',
    weight=3
).add_to(map)


def retriveCoordinates(location, dfAllLocations):
    for x in range(dfAllLocations.size):
        if location == dfAllLocations.iloc[x][1]:
            return dfAllLocations.iloc[x][3], dfAllLocations.iloc[x][2]
    return None

for x in range(10000):
    try:
        tooltip = "Price: $" + str(trac_data.iloc[x][7]) + "<br> Make & Model: " + str(
            trac_data.iloc[x][5]) + " " + str(trac_data.iloc[x][6])

        latitude, longitude = retriveCoordinates(trac_data.iloc[x][9], df2)
        folium.Marker(location=[longitude, latitude], icon=folium.Icon(color='black', icon='truck', prefix="fa"),
                      clustered_marker=True,
                      tooltip=tooltip, ).add_to(marker_cluster)
        temp = [longitude, latitude]
        heatMapArray.append(temp)

    except:
        pass

len(heatMapArray)

UniqueHeatMap= []

for x in heatMapArray:
    if(x not in UniqueHeatMap):
        UniqueHeatMap.append(x)


def add_weight(maparray, currentlocation):
    counter = 0
    for x in maparray:
        if(x==currentlocation):
            counter+=1
    return counter

for x in range(len(UniqueHeatMap)):
    try:
        UniqueHeatMap[x].append(add_weight(heatMapArray,UniqueHeatMap[x]))
    except:
        pass


count=0
for x in range(len(UniqueHeatMap)):
    count =count+  UniqueHeatMap[x][2]

len(heatMapArray)
len(UniqueHeatMap)


HeatMap(UniqueHeatMap,radius = 40).add_to(feature_group)
feature_group.add_to(map)
LayerControl().add_to(map)

legend_html = '''
                <div style="position: fixed;
                            bottom: 20px; left: 30px; width: 150px; height: 90px;
                            border:2px solid grey; z-index:9999; font-size:14px;
                            ">&nbsp; Work in Progress  <br>
                              &nbsp; Current Model &nbsp; <i class="fa fa-map-marker fa-2x" style="color:black"></i>
                </div>
                '''

map.get_root().html.add_child(folium.Element(legend_html))
map.save('HeatMap_V2.html')
print("Map Done ")
