#!/usr/bin/env python
# coding: utf-8

# import libs
import pandas as pd
import numpy as np

# import data
city_nl = pd.read_csv("../data/raw/nl3.csv", sep=',', index_col=[0])
df_pararius = pd.read_csv('../data/processed/df_pararius.csv', index_col=[0])
postcode = pd.read_csv("../data/raw/zipcode.csv", sep=',', index_col=[0])

# unique cities
par_cities = df_pararius['City'].unique()

# fill none
city_nl['Alternate Names'] = city_nl['Alternate Names'].fillna('None')


for i in par_cities:
    """
        for each city in the pararius database, it will check if there is a match
        on the alternative names of all cities in the netherlands, if yes, it will
        save the name of the city from ads to the all cities database
    """
    city_nl.loc[city_nl['Alternate Names'].str.contains(i), 'city'] = i

# Lorem
cities_par_x_nl = list(set(par_cities) - set(city_nl['city']))
# Lorem
cities_not_listed = df_pararius[df_pararius['City'].isin(cities_par_x_nl)]
# Lorem
df_city_coord = pd.merge(cities_not_listed[['City', 'Price']], postcode[[
                         'Plaats', 'Provincie', 'longitude', 'latitude']], left_on='City', right_on='Plaats', how='left')
# Lorem
df_city_coord_val = df_city_coord.groupby(['City', 'Provincie'])[
    ['longitude', 'latitude']].mean().reset_index()


def haversine(lat1, lon1, lat2, lon2):
    """
        calculate distance from 2 coordinates
    """
    earth_radius = 6371
    lat1, lon1, lat2, lon2 = np.radians([lat1, lon1, lat2, lon2])
    a = np.sin((lat2-lat1)/2.0)**2 + np.cos(lat1) * \
        np.cos(lat2) * np.sin((lon2-lon1)/2.0)**2
    return earth_radius * 2 * np.arcsin(np.sqrt(a))


# rename columns
df_city_coord_val = df_city_coord_val.rename(
    columns={'City': 'city', 'Provincie': 'Province'})

# join databases
df_results = pd.concat([city_nl, df_city_coord_val], 0).reset_index(drop=True)

# obvious people coordinates
df_results['latitude1'] = 51.907183
df_results['longitude1'] = 4.472815

# apply function
df_results['distance'] = haversine(
    df_results['latitude'],
    df_results['longitude'],
    df_results['latitude1'],
    df_results['longitude1']
)

# organize dataframe
df_results = df_results.sort_values('distance')

# for cities without cost, calculate it
df_results['cost'] = df_results['cost'].interpolate().fillna(
    df_results['cost'].mean())

# average_rents
average_rent = df_pararius.groupby(['City', 'Provincie'])[['Price']].mean()
average_rent = average_rent.reset_index().rename(columns={'Price': 'avg_rent'})

# merge results with average rents
df_final_result = pd.merge(
    df_results,
    average_rent,
    left_on=['city', 'Province'],
    right_on=['City', 'Provincie'],
    how='left')
# avg_costs
df_final_result['avg_costs'] = df_final_result['avg_rent'] + \
    df_final_result['cost']
# format coordinates
df_final_result['latitude'] = round(
    df_final_result['latitude'].astype(float), 5)
df_final_result['longitude'] = round(
    df_final_result['longitude'].astype(float), 5)
# format distance
df_final_result['distance'] = round(df_final_result['distance'], 2)
# format cost
df_final_result['cost'] = round(df_final_result['cost'], 2)
# format avg_rent
df_final_result['avg_rent'] = round(df_final_result['avg_rent'], 2)
# format avg_costs
df_final_result['avg_costs'] = round(df_final_result['avg_costs'], 2)
# columns accepted
final = df_final_result[['Alternate Names', 'city', 'Province', 'Population',
                         'distance', 'cost', 'avg_rent', 'avg_costs', 'latitude', 'longitude', ]].fillna('None')
# cities
par_cities = ["'s-Hertogenbosch", 'Alkmaar', 'Almere', 'Amersfoort', 'Amstelveen', 'Amsterdam', 'Apeldoorn', 'Arnhem', 'Breda', 'Bussum', 'Delft', 'Dordrecht', 'Eindhoven', 'Gouda',
              'Haarlem', 'Hilversum', 'Hoofddorp', 'Huizen', 'Leiden', 'Oegstgeest', 'Rijswijk', 'Rotterdam', 'Schiedam', 'Den Haag', 'Utrecht', 'Voorburg', 'Zaandam', 'Zeist', 'Zoetermeer']
df_final_result = final[final['city'].isin(par_cities)].reset_index(drop=True)

# save dates
df_final_result.to_csv('../app/costs.csv')
df_pararius = pd.read_csv('../data/processed/df_pararius.csv', index_col=[0])
df_pararius.to_csv('../app/df_pararius.csv')
df_results.to_csv("../data/processed/nl3.csv")
