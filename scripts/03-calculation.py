"""
    Who: Ericson Mattoso
    When: 04/nov/2021
    What: This script is responsable calculate houses priority
    Why: This calculation will help users to find a best deal house
    Where: data comes from previous dataframes. 
    How: calculates based a weighted variables
"""
# libs
import pandas as pd
from scipy import spatial

# read data from our database
df_pararius_coo = pd.read_csv(
    '../data/processed/df_coo_pararius.csv', index_col=[0])
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
    zip(df_pararius_coo['latitude'], df_pararius_coo['longitude']))
coordinates_2 = list(zip(stations['latitude'], stations['longitude']))

# normalizing coordinates
tree = spatial.KDTree(coordinates_2)
distance = []

# calculate distance from station to postcodes
for i in range(len(df_pararius_coo)):
    teste = coordinates_1[i]
    distance.append(tree.query(teste)[0])

# getting variables
df_pararius_coo['train'] = distance
clc_area = df_pararius_coo['surface-area']
clc_room = df_pararius_coo['number-of-rooms']
clc_garden = df_pararius_coo['garden-surface-area']
clc_price = df_pararius_coo['price']
clc_train = df_pararius_coo['train']

# calculation of priority
df_pararius_coo['deal'] = (
    (clc_area + clc_room + clc_garden) / (clc_price + clc_train))
# saving the data
df_pararius_coo.to_csv('../data/processed/df_coo_pararius.csv')
