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
import numpy as np
from datetime import date
today = date.today()

# import data
cost_living = pd.read_csv(
    "../data/raw/cost_living.csv", sep=',', index_col=[0])
df_pararius = pd.read_csv('../data/processed/df_housing.csv', index_col=[0])

# Add cost of living
df_city_coord = pd.merge(df_pararius, cost_living[['province', 'city', 'cost', 'latitude_city', 'longitude_city',
                         'alternate names', 'population', 'distance']], left_on=['provincie', 'city'], right_on=['province', 'city'], how='left')

# remove the char '\n'
cols_to_check = df_city_coord.columns
df_city_coord[cols_to_check] = df_city_coord[cols_to_check].replace(
    {'\n': ''}, regex=True)


def clean_contet(column):
    return df_city_coord[column].astype(str).str.replace("\D", "", regex=True).replace("", 0, regex=True).astype(int)


df_city_coord["dimensions living area"] = clean_contet(
    "dimensions living area")
df_city_coord["outdoor garden"] = clean_contet("outdoor garden")
df_city_coord["price"] = clean_contet("price")

# remove the df_city_coord
df_city_coord = df_city_coord.replace([np.inf, -np.inf], np.nan)

# fill empty and change type
df_city_coord['price'] = df_city_coord['price'].fillna(0).astype(int)
df_city_coord['outdoor garden'] = df_city_coord['outdoor garden'].fillna(
    0).astype(int)
df_city_coord['distance'] = df_city_coord['distance'].fillna(0).astype(int)
df_city_coord['dimensions living area'] = df_city_coord['dimensions living area'].fillna(
    0).astype(int)
df_city_coord['layout number of rooms'] = df_city_coord['layout number of rooms'].fillna(
    0).astype(int)


def fixing_time_delta(df, time, my_ofset):
    """
        this function will get and transform string into date format
    """
    # if contains week or month
    fixing_time_delta = df.loc[df['transfer offered since'].str.contains(
        time, na=False), 'transfer offered since']
    # removing unwanted char
    fixing_time_delta = fixing_time_delta.str.replace(
        "\D", "", regex=True).astype(int)
    # calculate when posted vs today
    fixing_time_delta = today - fixing_time_delta.apply(my_ofset)
    # formating date
    fixing_time_delta = pd.to_datetime(
        fixing_time_delta).dt.strftime('%d-%m-%Y')
    # replace date
    df.loc[df['transfer offered since'].str.contains(
        time, na=False), 'transfer offered since'] = fixing_time_delta
    return df


try:
    df_city_coord = fixing_time_delta(df_city_coord, "week", pd.offsets.Week)
    df_city_coord = fixing_time_delta(
        df_city_coord, "month", pd.offsets.MonthBegin)


except:
    print('erro')
    pass

# removing unwanted char
df_city_coord['transfer available'] = df_city_coord['transfer available'].str.replace(
    "From", "")

# removing unwanted char
df_city_coord['transfer available'] = df_city_coord['transfer available'].str.replace(
    "Immediately|In consultation", str(today))

# formating char
df_city_coord['transfer available'] = pd.to_datetime(
    df_city_coord['transfer available']).dt.strftime('%d-%m-%Y')

# formating title
df_city_coord['title'] = df_city_coord['title'].str.replace("For rent: ", "")
df_city_coord['url'] = 'https://www.pararius.com'+df_city_coord['link']
df_city_coord['image'] = "<a href=" + df_city_coord['url'] + " target='blank'><img src=" + \
    df_city_coord['img'] + " title='rent' width='150' height='100'/></a>"

# Save
df_city_coord.to_csv('../data/processed/df_housing.csv')
cost_living['distance'] = cost_living['distance'].astype(int)
cost_living.drop(columns=['coordinates']).to_csv('../app/cost_living.csv')
