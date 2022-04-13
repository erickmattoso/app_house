#!/usr/bin/env python
# coding: utf-8
"""
    Who: Ericson Mattoso
    When: 12/April/2022
    What: This script is responsable calculate houses priority
    Why: This calculation will help users to find a best deal house
    Where: data comes from previous dataframes. 
    How: calculates based a weighted variables
"""
import pandas as pd
from scipy import spatial
import numpy as np

# read data from our database
df_housing_coo = pd.read_csv('../data/processed/df_housing.csv', index_col=[0])

# read train station data in europe
link1 = 'https://github.com/trainline-eu/stations/blob/master/stations.csv'
link2 = 'https://raw.githubusercontent.com/trainline-eu/stations/master/stations.csv'

# try to read and then save the data
try:
    stations = pd.read_csv(link2, sep=';', low_memory=False)
    stations.to_csv('../data/raw/stations.csv')

# in case of the data is not available, read local file
except:
    print('local')
    stations = pd.read_csv('../data/raw/stations.csv',
                           sep=';', low_memory=False)

# read data from NL
stations = stations[stations['country'] ==
                    'NL'][['name', 'latitude', 'longitude']]

# valid info
stations = stations[stations['latitude'].notna()].reset_index(drop=True)

# getting coordinates from stations and our postcodes
coordinates_1 = list(
    zip(df_housing_coo['latitude'], df_housing_coo['longitude']))
coordinates_2 = list(zip(stations['latitude'], stations['longitude']))

# normalizing coordinates
tree = spatial.KDTree(coordinates_2)
distance = []

# calculate distance from station to postcodes
for i in range(len(df_housing_coo)):
    teste = coordinates_1[i]
    distance.append(tree.query(teste)[0])

# getting variables
df_housing_coo['train'] = distance

df_housing_coo["OP_latitude"] = 51.9071833
df_housing_coo["OP_longitude"] = 4.4728155


def haversine(lat1, lon1, lat2, lon2):
    """
        calculate distance from 2 coordinates
    """
    earth_radius = 6371
    lat1, lon1, lat2, lon2 = np.radians([lat1, lon1, lat2, lon2])
    a = np.sin((lat2-lat1)/2.0)**2 + np.cos(lat1) * \
        np.cos(lat2) * np.sin((lon2-lon1)/2.0)**2
    return earth_radius * 2 * np.arcsin(np.sqrt(a))


df_housing_coo['distance_house'] = haversine(
    df_housing_coo['OP_latitude'],
    df_housing_coo['OP_longitude'],
    df_housing_coo['latitude'],
    df_housing_coo['longitude']
)

df_housing_coo = df_housing_coo.replace([np.inf, -np.inf], np.nan)

clc_area = df_housing_coo['dimensions living area'].astype(int).fillna(0)
clc_room = df_housing_coo['layout number of rooms'].astype(int).fillna(0)
clc_garden = df_housing_coo['outdoor garden'].astype(int).fillna(0)
clc_price = df_housing_coo['price'].astype(int).fillna(0)
clc_train = df_housing_coo['train']
clc_distance_house = df_housing_coo['distance_house']

# Calculate best deal
df_housing_coo['deal'] = (
    (clc_area + clc_room + clc_garden) / (clc_price + clc_train + clc_distance_house))

print(len(df_housing_coo))
df_housing_coo = df_housing_coo[df_housing_coo['transfer rental agreement']
                                != "Temporary rental"]
print(len(df_housing_coo))

df_housing_coo = df_housing_coo.drop(
    columns=['unnamed: 0']).reset_index(drop=True)

df_housing_coo.to_csv('../app/df_housing_app.csv')
