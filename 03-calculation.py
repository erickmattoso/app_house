#!/usr/bin/env python
# coding: utf-8

# # imports

# In[1]:


import pandas as pd
from scipy import spatial


# # read file

# In[2]:


df_pararius_coo = pd.read_csv('app/df_coo_pararius.csv', index_col=[0])


# # Distance from station
# How far is this house from a public train station?

# ## read csv with station location

# In[3]:


link1 = 'https://github.com/trainline-eu/stations/blob/master/stations.csv'
link2 = 'https://raw.githubusercontent.com/trainline-eu/stations/master/stations.csv'

try:
    stations = pd.read_csv(link2, sep=';', low_memory=False)
    stations.to_csv('data/processed/stations.csv')
except:
    print('local')
    stations = pd.read_csv('data/processed/stations.csv',
                           sep=';', low_memory=False)


# ## calculating distance a train station from our houses

# In[4]:


stations = stations[stations['country'] ==
                    'NL'][['name', 'latitude', 'longitude']]
stations = stations[stations['latitude'].notna()].reset_index(drop=True)

coordinates_1 = list(
    zip(df_pararius_coo['latitude'], df_pararius_coo['longitude']))
coordinates_2 = list(zip(stations['latitude'], stations['longitude']))
tree = spatial.KDTree(coordinates_2)

distance = []
for i in range(len(df_pararius_coo)):
    teste = coordinates_1[i]
    distance.append(tree.query(teste)[0])

df_pararius_coo['train'] = distance


# # Calculate best deal

# In[5]:


clc_area = df_pararius_coo['surface-area']
clc_room = df_pararius_coo['number-of-rooms']
clc_garden = df_pararius_coo['garden-surface-area']
clc_price = df_pararius_coo['price']
clc_train = df_pararius_coo['train']

# df_pararius_coo['deal'] = 100 * ((3*clc_area + clc_room + 2*clc_garden) / (3*clc_price + 2*clc_train))
df_pararius_coo['deal'] = (
    (clc_area + clc_room + clc_garden) / (clc_price + clc_train))


# # Save results

# In[6]:


df_pararius_coo.to_csv('app/df_coo_pararius.csv')


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:
