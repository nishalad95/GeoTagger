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



def get_latitude_longitude(place_name):
    """
    Gets coordinates and address for a given place name using geopy
    """
    # Create geo_locator object instance

    # place_name = "Champ de Mars, Paris, France"
    # Attempt to obtain geo data for given place name
    try:
        geo_locator = Nominatim(user_agent="myGeocoder")
        time.sleep(1)
        location = geo_locator.geocode(place_name)
    except Exception:
        # return None
        return pd.Series([None, None])

    if not location:
        # return None
        return pd.Series([None, None])

    # return float(location.latitude), float(location.longitude)
    return pd.Series([location.latitude, location.longitude])


def convert_to_string(x):
    return str(x)


def extract_day_from_tweets(df, date):
    df = df[df['created_at'].astype(str).str.contains(date)] 
    return df

def plot_and_save_map(df, filename, data_path):
    """
    Extract coordinates, plot on an interactive map and save to html file
    """

#    N = 3000
#    lat_long_df = df.head(N)
    lat_long_df = df
    #seed = int(np.random.uniform() * 100)
    #df = df.sample(frac=0.6, replace=False, random_state=seed)
    #print("LENGTH OF SAMPLED DF " + str(len(df)))
    #lat_long_df = df

    #lat_long_df[['geo_lat', 'geo_long']] = lat_long_df['location'].apply(lambda x: get_latitude_longitude(x))
    #lat_long_df['location'] = lat_long_df['location'].apply(lambda x: convert_to_string(x))
    #lat_long_df['geo_lat'] = lat_long_df['geo_lat'].apply(lambda x: convert_to_string(x))

    # # drop NaNs and save latitude longitude data to csv
    #lat_long_df.dropna(subset=['geo_lat'])
    #lat_long_df = lat_long_df.loc[lat_long_df['geo_lat'] != 'NaN']
    #lat_long_df = lat_long_df.loc[lat_long_df['geo_lat'] != 'nan']
    #lat_long_df.to_csv(data_path, index=False)   

 
    print()
    print("LAT LONG DF:")
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

    iconCreateFunction = ('function(cluster) {'
                'var childCount = cluster.getChildCount();' 
                'var c = " marker-cluster-medium";'
#                'if (childCount < 50) {'
#                    'c += "large";'
#                '} else if (childCount < 300) {'
#                    'c += "medium";'
#                '} else {'
#                    'c += "small";'
#                '}'
                'return new L.DivIcon({ html: "<div><span>" + childCount + "</span></div>", className: "marker-cluster" + c, iconSize: new L.Point(35, 35) });}')    



    # Density layer
    FastMarkerCluster(
    data=list(zip(lat_long_df['geo_lat'].values, lat_long_df['geo_long'].values)), 
    name='Density', 
    icon_create_function=iconCreateFunction,
    callback=callback
    ).add_to(map)
   

    # Sentiment layer
    sentiment_layer = folium.FeatureGroup(name="Sentiment")
    for index, row in lat_long_df.iterrows():
        sentiment_layer.add_child(folium.CircleMarker(
        [row['geo_lat'], row['geo_long']], 
        radius=3,
        color='clear', 
        fill_color=row['hex_colour'], 
        fill='true', 
        fill_opacity=0.75, 
        popup=('Sentiment: ' + str(row['sentiment'])[0:5] + '\n Classification: ' + str(row['labels']) ) 
        )).add_to(map)
    map.add_child(sentiment_layer, name='Sentiment')



    # Classification layer
    classification_layer = folium.FeatureGroup(name="Classification")
    for index, row in lat_long_df.iterrows():
        classification_layer.add_child(folium.CircleMarker(
        [row['geo_lat'], row['geo_long']], 
        radius=3,
        color='clear', 
        fill_color=row['classification_colour'], 
        fill='true', 
        fill_opacity=0.75, 
        popup=('Sentiment: ' + str(row['sentiment'])[0:5] + '\n Classification: ' + str(row['labels']) ) 
        )).add_to(map)
    map.add_child(classification_layer, name='Classification')


    # heatmap layer
    lat_long_matrix = lat_long_df[['geo_lat', 'geo_long']].as_matrix()
    map.add_child(
    HeatMap(lat_long_matrix, 
    radius=12,
    name='Heatmap')
    )


    folium.LayerControl().add_to(map)
    map.save(filename)





#####################
# RUN GEOTAGGER
#####################

start = time.time()


# prepare the dataset we wish to analyse
dataset = "EvolutionMaps/FinalReport/Brexit/Brexit_Geotagger_Final_Jan31_14422_samples.csv"

# process the data
df = pd.read_csv(dataset)
print("ORIGINAL FULL DATASET")
print(df)
print(len(df))


# extract day by day
#date = "2020-02-22"
#day_df = extract_day_from_tweets(df, date)
#print("SINGLE DAY DATASET")
#print(day_df)
#print(len(day_df))


# run geotagger and save UI
save_data_path="geotagger_improvements_test.csv"
save_map_path = "Brexit_Geotagger_Final_Jan31_14422_samples.html"
plot_and_save_map(df, save_map_path, save_data_path)


end = time.time()
print("Execution time: " + str((end - start)/60) + " mins")
