import pandas as pd
import numpy as np
pop = pd.read_csv("../data/raw/nl3.csv", sep=',', index_col=[0])
dash = pd.read_csv('../data/processed/df_pararius.csv', index_col=[0])
postcode = pd.read_csv("../data/raw/zipcode.csv", sep=',', index_col=[0])
searchfor = dash['City'].unique()
pop['Alternate Names'] = pop['Alternate Names'].fillna('None')
for i in searchfor:
    pop.loc[pop['Alternate Names'].str.contains(i), 'city'] = i
pop['city'] = pop['city'].fillna(pop['city'])
ast = list(set(searchfor) - set(pop['city']))
test = dash[dash['City'].isin(ast)]
postcode = postcode.rename(columns={'Plaats': 'City'})
aaa = pd.merge(test[['City', 'Price']], postcode[['City', 'Provincie',
               'longitude', 'latitude']], left_on='City', right_on='City', how='left')
ccc = aaa.groupby(['City', 'Provincie'])[
    ['longitude', 'latitude']].mean().reset_index()


def haversine(lat1, lon1, lat2, lon2):
    earth_radius = 6371
    lat1, lon1, lat2, lon2 = np.radians([lat1, lon1, lat2, lon2])
    a = np.sin((lat2-lat1)/2.0)**2 + np.cos(lat1) * \
        np.cos(lat2) * np.sin((lon2-lon1)/2.0)**2
    return earth_radius * 2 * np.arcsin(np.sqrt(a))


ccc['latitude1'] = 51.907183
ccc['longitude1'] = 4.472815
ccc['distance'] = haversine(
    ccc['latitude'], ccc['longitude'], ccc['latitude1'], ccc['longitude1'])
ccc = ccc.rename(columns={'City': 'city', 'Provincie': 'Province'})
finaleira = pd.concat([pop, ccc], 0).reset_index(drop=True)


def haversine(lat1, lon1, lat2, lon2):
    earth_radius = 6371
    lat1, lon1, lat2, lon2 = np.radians([lat1, lon1, lat2, lon2])
    a = np.sin((lat2-lat1)/2.0)**2 + np.cos(lat1) * \
        np.cos(lat2) * np.sin((lon2-lon1)/2.0)**2
    return earth_radius * 2 * np.arcsin(np.sqrt(a))


finaleira['latitude1'] = 51.907183
finaleira['longitude1'] = 4.472815
finaleira['distance'] = haversine(
    finaleira['latitude'], finaleira['longitude'], finaleira['latitude1'], finaleira['longitude1'])
finaleira = finaleira.sort_values('distance')
finaleira['cost'] = finaleira['cost'].interpolate().fillna(
    finaleira['cost'].mean())
finaleira.to_csv("../data/raw/nl3.csv")
average_rent = dash.groupby(['City', 'Provincie'])[['Price']].mean(
).reset_index().rename(columns={'Price': 'avg_rent'})
fim = pd.merge(finaleira, average_rent, left_on=[
               'city', 'Province'], right_on=['City', 'Provincie'], how='left')
fim['avg_costs'] = fim['avg_rent'] + fim['cost']
fim['latitude'] = round(fim['latitude'].astype(float), 5)
fim['longitude'] = round(fim['longitude'].astype(float), 5)
fim['distance'] = round(fim['distance'], 2)
fim['cost'] = round(fim['cost'], 2)
fim['avg_rent'] = round(fim['avg_rent'], 2)
fim['avg_costs'] = round(fim['avg_costs'], 2)
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
final[final['city'].isin(searchfor)].reset_index(
    drop=True).to_csv('../app/costs.csv')
dash = pd.read_csv('../data/processed/df_pararius.csv', index_col=[0])
dash.to_csv('../app/df_pararius.csv')
