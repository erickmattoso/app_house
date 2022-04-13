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
from bs4 import BeautifulSoup
import glob
import os
import pandas as pd
import requests


def postnl_scrape(cep):
    """
        This function shall request coordinates from postcodebijadres
    """
    # creates link
    url = 'https://postcodebijadres.nl/' + cep
    # create header to simulate human behaviour on scrape
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0"}
    # scrape
    soup = BeautifulSoup(requests.get(
        url, headers=headers).content, "html.parser")
    # html as string
    return soup


df_zipcode = pd.read_csv('../data/raw/zipcode.csv', index_col=[0])
df_housing = pd.read_csv("../data/processed/all_content.csv", index_col=[0])
df_housing['postcode'] = df_housing['location'].str[:7].str.replace(" ", "")
# what are the zipcodes we have scrapped?
temp1 = df_housing['postcode'].unique()
# what are those we already have the coordinates?
temp2 = df_zipcode['postcode'].unique()
# what is new?
cep_zip = list(set(temp1) - set(temp2))
# how many new zipcodes without coordidates we have
print(len(cep_zip))
# empty variables
zipcode = pd.DataFrame({})
description_1 = {}
# read each new zipcode
for cep in cep_zip:
    # load the scraper
    soup = postnl_scrape(cep)
    try:
        # get first table
        split0 = soup.find_all(
            'table', {"class": "table table-bordered mt-3"})[0]
        # get second table
        split1 = soup.find_all(
            'table', {"class": "table table-bordered mt-3"})[1]
        # coordinates
        lat = split1.find_all('td')[1].text
        lon = split1.find_all('td')[3].text
        # save on dict
        description_1.update({'latitude': lat, 'longitude': lon})
        # each row of the table
        for num in range(9):
            # get key and value
            split0_key = split0.find_all('th')[num].text
            split0_val = split0.find_all('td')[num].text
            # save on dict
            description_1.update({split0_key: split0_val})
        # dict into df
        zipcode_ = pd.DataFrame(description_1, index=[0])
        # add on the df
        zipcode_['postcode'] = zipcode_['Postcode'].str.replace(" ", "")
        df_zipcode = pd.concat([df_zipcode, zipcode_], 0)
    except:
        print('#####################################', cep)
        pass
# add new info into the housing dataframe
zipcode_housing_coo = pd.merge(
    df_housing, df_zipcode, how='left', on='postcode')
col = (map(lambda x: x.lower(), zipcode_housing_coo.columns))
col = list(col)
zipcode_housing_coo.columns = col
zipcode_housing_coo = zipcode_housing_coo.rename(columns={"plaats": "city"})
# saving data
zipcode_housing_coo.to_csv('../data/processed/df_housing.csv')
df_zipcode.to_csv('../data/raw/zipcode.csv')
