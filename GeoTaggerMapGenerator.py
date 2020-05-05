import tarfile
import pandas as pd
import csv
from geopy.geocoders import Nominatim
import geopy
import folium
from folium import plugins
from folium import Icon
from folium.plugins import FastMarkerCluster
from folium.plugins import HeatMap
import time
import re
import ast
from datetime import datetime
import numpy as np




def plot_and_save_map(df, filename):
#    seed = int(np.random.uniform() * 100)
#    df = df.sample(frac=0.5, replace=False, random_state=seed)
#    print("LENGTH OF SAMPLED DF " + str(len(df)))

    lat_long_df = df
 
    print()
    print(lat_long_df)
    print(len(lat_long_df))


    # create map
    map = folium.Map(
        location=[53.8, 4.5],
        tiles='cartodbpositron',
        zoom_start=3,
    )

    # create layers
    callback = ('function (row) {' 
                'var marker = L.marker(new L.LatLng(row[0], row[1]), {color: "#8a8a8a"});'
                'var icon = L.AwesomeMarkers.icon({'
                "icon: 'user',"
                "iconColor: 'white',"
                "markerColor: 'black',"
                "prefix: 'glyphicon',"
                "extraClasses: 'fa-rotate-0'"
                    '});'
                'marker.setIcon(icon);'
                'return marker};')
                #"var popup = L.popup({maxWidth: '300'});"
                #"const display_text = {text: row[2]};"
                #"var mytext = $(`<div id='mytext' class='display_text' style='width: 100.0%; height: 100.0%;'> ${display_text.text}</div>`)[0];"
                #"popup.setContent(mytext);"
                #"marker.bindPopup(popup);"
                #'return marker};')



    # Density layer
    FastMarkerCluster(data=list(zip(lat_long_df['geo_lat'].values, lat_long_df['geo_long'].values)), name='Density', callback=callback).add_to(map)
   

    # Sentiment layer
    sentiment_layer = folium.FeatureGroup(name="Sentiment")
    for index, row in lat_long_df.iterrows():
        sentiment_layer.add_child(folium.CircleMarker([row['geo_lat'], row['geo_long']], radius=6, color=row['hex_colour'], fill=True, fill_opacity=0.6, popup=('Sentiment: ' + str(row['sentiment'])[0:5] + '\n Classification: ' + str(row['labels']) ) )).add_to(map)
    map.add_child(sentiment_layer, name='Sentiment')



    # Classification layer
    classification_layer = folium.FeatureGroup(name="Classification")
    for index, row in lat_long_df.iterrows():
        classification_layer.add_child(folium.CircleMarker([row['geo_lat'], row['geo_long']], radius=6, color=row['classification_colour'], fill=True, fill_opacity=0.3, popup=('Sentiment: ' + str(row['sentiment'])[0:5] + '\n Classification: ' + str(row['labels']) ) )).add_to(map)
    map.add_child(classification_layer, name='Classification')




    # heatmap layer
    # convert to (n, 2) nd-array format for heatmap
    lat_long_matrix = lat_long_df[['geo_lat', 'geo_long']].as_matrix()
    map.add_child(HeatMap(lat_long_matrix, radius=12, name='Heatmap'))

    folium.LayerControl().add_to(map)
    map.save(filename)



#####################
# RUN GEOTAGGER
#####################

start = time.time()

# prepare the dataset we wish to analyse
dataset = "Brexit_Jan29_Final_Geotagger_sentiment_userclass_colour_noNans_17846_samples.csv"

# process the data
df = pd.read_csv(dataset)

# run geotagger and save UI
save_map_path = "EvolutionMaps/FinalReport/Brexit/Brexit_jan29.html"
plot_and_save_map(df, save_map_path)


end = time.time()
print("Execution time: " + str((end - start)/60) + " mins")
