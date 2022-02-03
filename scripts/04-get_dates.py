"""
    Who: Ericson Mattoso
    When: 04/nov/2021
    What: This script is responsable calculate houses priority
    Why: This calculation will help users to find a best deal house
    Where: data comes from previous dataframes. 
    How: calculates based a weighted variables
    todo: moving processed files that should be on raw
"""

# libs
from bs4 import BeautifulSoup
from datetime import date
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
today = date.today()

# read data
df_pararius = pd.read_csv('../data/processed/df_pararius.csv', index_col=[0])
house_temp = pd.read_csv('../data/raw/house_temp.csv', index_col=[0])

# get unique urls in each dataframe
temp1 = df_pararius['url'].unique()
temp2 = house_temp['url'].unique()

# get only new links that are not saved on our database
urls = list(set(temp1) - set(temp2))

# Print how many new urls we have now. This is the number of links we need to scrape
print(len(urls))


def key_val(text):
    part = html_soup.find("dt", text=text)
    key = (part.text.strip())
    val = (part.findNext("dd").text.strip())
    return key, val


def scrape_web(url):
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.implicitly_wait(30)
    driver.get(url)
    html_soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.close()
    return html_soup


# variables
not_available = []
description_2 = []
# This is going in each page to save the dates of
i = 0

for url in urls:
    # flag
    print(">>>>>>>>>", i, url)
    description_1 = {}
    try:
        html_soup = scrape_web(url)
        key1, val1 = key_val("Offered since")
        key2, val2 = key_val("Available")
        description_1.update({
            'url': url,
            key1: val1,
            key2: val2,
        })
        description_2.append(description_1)
        i = i+1
        print('done')
        print()
    except:
        print('error')
        pass
house_temp_ = pd.DataFrame(description_2)
house_temp = pd.concat([house_temp, house_temp_], 0)


def fixing_time_delta(df, time, my_ofset):
    """
        this function will get and transform string into date format
    """
    # if contains week or month
    fixing_time_delta = df.loc[df['Offered since'].str.contains(
        time, na=False), 'Offered since']
    # removing unwanted char
    fixing_time_delta = fixing_time_delta.str.replace(
        "\D", "", regex=True).astype(int)
    # calculate when posted vs today
    fixing_time_delta = today - fixing_time_delta.apply(my_ofset)
    # formating date
    fixing_time_delta = pd.to_datetime(
        fixing_time_delta).dt.strftime('%d-%m-%Y')
    # replace date
    df.loc[df['Offered since'].str.contains(
        time, na=False), 'Offered since'] = fixing_time_delta
    return df


# applying function
try:
    house_temp = fixing_time_delta(house_temp, "week", pd.offsets.Week)
    house_temp = fixing_time_delta(house_temp, "month", pd.offsets.MonthBegin)
except:
    print('erro')
    pass

# removing unwanted char
house_temp['Available'] = house_temp['Available'].str.replace("From", "")
# removing unwanted char
house_temp['Available'] = house_temp['Available'].str.replace(
    "Immediately|In consultation", str(today))
# formating char
house_temp['Available'] = pd.to_datetime(
    house_temp['Available']).dt.strftime('%d-%m-%Y')
# remove duplicates
house_temp = house_temp.drop_duplicates(subset=['url']).reset_index(drop=True)
# save results into original df
result = pd.merge(df_pararius, house_temp, how='left', on='url')

# save only certain columns
result2 = result[[
    'deal',
    'garden-surface-area',
    'img',
    'price',
    'link',
    'agency',
    'surface-area',
    'interior',
    'latitude',
    'longitude',
    'number-of-rooms',
    'Plaats',
    'Provincie',
    'url',
    'date',
    'status',
    'irl',
    'image',
    'address',
    'street',
    'Offered since',
    'Available',
]]
# rename columns
result2 = result2.rename(columns={
    'img': 'Add',
    'price': 'Price',
    'Plaats': 'City',
    'surface-area': 'Area',
    'number-of-rooms': 'Rooms',
    'garden-surface-area': 'Garden',
    'Offered since': 'Offered',
    'Available': 'Available', })
# Save
result2.to_csv('../data/processed/df_pararius.csv')
house_temp.to_csv('../data/raw/house_temp.csv')
