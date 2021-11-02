#!/usr/bin/env python
# coding: utf-8

# https://public.opendatasoft.com/explore/dataset/geonames-all-cities-with-a-population-1000/export/?disjunctive.cou_name_en&sort=name&location=7,51.62484,6.58081&basemap=jawg.streets
# 

# In[1]:


import pandas as pd
import numpy as np
pd.set_option('display.max_columns', None)


# In[2]:


pop = pd.read_csv("data/processed/nl3.csv", sep=',',index_col=[0])
dash = pd.read_csv("app/df_coo_pararius.csv")
zio = pd.read_csv("data/processed/zipcodeZ.csv", sep=',',index_col=[0])


# In[3]:


searchfor = dash['Plaats'].unique()
pop['Alternate Names'] = pop['Alternate Names'].fillna('None')
for i in searchfor:
    pop.loc[pop['Alternate Names'].str.contains(i),'city'] = i
pop['city'] = pop['city'].fillna(pop['city'])


# In[4]:


ast  =  list(set(searchfor) - set(pop['city']))


# In[5]:


test = dash[dash['Plaats'].isin(ast)]
aaa = pd.merge(test[['Plaats','price']],zio[['Plaats','Provincie','longitude','latitude']], left_on='Plaats', right_on='Plaats',how='left')
ccc = aaa.groupby(['Plaats','Provincie'])[['longitude','latitude']].mean().reset_index()


# In[6]:


def haversine(lat1, lon1, lat2, lon2):
    earth_radius=6371
    lat1, lon1, lat2, lon2 = np.radians([lat1, lon1, lat2, lon2])
    a = np.sin((lat2-lat1)/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin((lon2-lon1)/2.0)**2
    return earth_radius * 2 * np.arcsin(np.sqrt(a))

ccc['latitude1'] = 51.907183
ccc['longitude1'] = 4.472815
ccc['distance'] = haversine(ccc['latitude'], ccc['longitude'], ccc['latitude1'], ccc['longitude1'])
ccc = ccc.rename(columns={'Plaats':'city','Provincie':'Province'})


# In[7]:


finaleira = pd.concat([pop,ccc],0).reset_index(drop=True)


# In[8]:


import numpy as np
def haversine(lat1, lon1, lat2, lon2):
    earth_radius=6371
    lat1, lon1, lat2, lon2 = np.radians([lat1, lon1, lat2, lon2])
    a = np.sin((lat2-lat1)/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin((lon2-lon1)/2.0)**2
    return earth_radius * 2 * np.arcsin(np.sqrt(a))

finaleira['latitude1'] = 51.907183
finaleira['longitude1'] = 4.472815
finaleira['distance'] = haversine(finaleira['latitude'], finaleira['longitude'], finaleira['latitude1'], finaleira['longitude1'])
finaleira = finaleira.sort_values('distance')


# In[9]:


finaleira['cost'] = finaleira['cost'].interpolate().fillna(finaleira['cost'].mean())


# In[10]:


finaleira.to_csv("data/processed/nl3.csv")


# In[11]:


average_rent = dash.groupby(['Plaats','Provincie'])[['price']].mean().reset_index().rename(columns={'price':'avg_rent'})
fim = pd.merge(finaleira,average_rent,left_on=['city','Province'],right_on=['Plaats','Provincie'],how='left')
fim['avg_costs'] = fim['avg_rent'] + fim['cost']


# In[12]:


fim['latitude' ] = round(fim['latitude'].astype(float),5)
fim['longitude'] = round(fim['longitude'].astype(float),5)
fim['distance'] = round(fim['distance'],2)
fim['cost'] = round(fim['cost'],2)
fim['avg_rent'] = round(fim['avg_rent'],2)
fim['avg_costs'] = round(fim['avg_costs'],2)


# In[14]:


final = fim[[
    'Alternate Names',
    'city',
    'Province',
    'Population',
    'distance',
    'cost',
    'avg_rent',
    'avg_costs',
    'latitude',
    'longitude',
]].fillna('None')
final


# In[15]:


searchfor = ["'s-Hertogenbosch",
 'Alkmaar',
 'Almere',
 'Amersfoort',
 'Amstelveen',
 'Amsterdam',
 'Apeldoorn',
 'Arnhem',
 'Breda',
 'Bussum',
 'Delft',
 'Dordrecht',
 'Eindhoven',
 'Gouda',
 'Haarlem',
 'Hilversum',
 'Hoofddorp',
 'Huizen',
 'Leiden',
 'Oegstgeest',
 'Rijswijk',
 'Rotterdam',
 'Schiedam',
 'Den Haag',
 'Utrecht',
 'Voorburg',
 'Zaandam',
 'Zeist',
 'Zoetermeer']


# In[18]:


final[final['city'].isin(searchfor)].reset_index(drop=True).to_csv('app/costs.csv')


# In[19]:


pd.read_csv('app/costs.csv', index_col=[0])

