"""
    Who: Ericson Mattoso
    When: 04/nov/2021
    What: This script is responsable to take each house zipcode and find the coordinates for it.
    Why: Coordinates are necessary to print the addesses on our map
    Where: Zipcode comes from Pararius.nl and Coordinates comes from postcodebijadres.nl
    How: scrapping data through BeautifulSoup
"""
# Libs
from bs4 import BeautifulSoup
import glob
import os
import pandas as pd
import requests

# list all files
list_of_files = glob.glob("../data/temp/df_pararius_*.csv")
# get the newest
latest_file = max(list_of_files, key=os.path.getctime)
# read the newest file
df_pararius = pd.read_csv(latest_file, index_col=[0])
# get all zipcodes in our db
df_zipcode = pd.read_csv('../data/raw/zipcode.csv', index_col=[0])
# what are the zipcodes we have scrapped?
temp1 = df_pararius['postcode'].unique()
# what are those we already have the coordinates?
temp2 = df_zipcode['postcode'].unique()
# what is new?
cep_zip = list(set(temp1) - set(temp2))
# how many new zipcodes without coordidates we have
print(len(cep_zip))


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
        zipcode = pd.concat([zipcode, zipcode_], 0)
        print(cep)
    except:
        print('#####################################', cep)
        pass

try:
    # removing unwanted char
    zipcode['Straat'] = zipcode['Straat'].str.replace('\n', "", regex=True)
    # removing unwanted char
    zipcode['Postcode'] = zipcode['Postcode'].str.replace(' ', "", regex=True)
    # removing unwanted char
    zipcode = zipcode.rename(columns={'Postcode': 'postcode'})
    # add on the original df
    zipcode = pd.concat([zipcode, df_zipcode], 0).reset_index(drop=True)
    # remove duplicates
    zipcode = zipcode.drop_duplicates(
        subset=['postcode']).reset_index(drop=True)
except:
    # any new zipcode, just go forward
    zipcode = df_zipcode.copy()
# add new info into the pararius dataframe
zipcode_pararius_coo = pd.merge(
    df_pararius, zipcode, how='left', on='postcode')

# fill with zeros
zipcode_pararius_coo = zipcode_pararius_coo.fillna(
    0).drop_duplicates(subset=['irl']).reset_index(drop=True)

# cleaning data
zipcode_pararius_coo.loc[zipcode_pararius_coo['interior']
                         == 0, 'interior'] = 'Upholstered'
# cleaning data
zipcode_pararius_coo.loc[zipcode_pararius_coo['status']
                         == 0, 'status'] = 'Free'
# cleaning data
zipcode_pararius_coo['url'] = 'https://www.pararius.com' + \
    zipcode_pararius_coo['irl']
# cleaning data
zipcode_pararius_coo['link'] = "<a target='_blank' href=" + (zipcode_pararius_coo['url']).astype(
    str) + ">" + (zipcode_pararius_coo['street']).astype(str) + "</a>"
# cleaning data
zipcode_pararius_coo['img'] = "<a href=" + zipcode_pararius_coo['url'] + " target='blank'><img src=" + \
    zipcode_pararius_coo['image'] + \
    " title='rent' width='150' height='100'/></a>"
# saving data
zipcode_pararius_coo.to_csv('../data/processed/df_coo_pararius.csv')
zipcode.to_csv('../data/raw/zipcode.csv')
