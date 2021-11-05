"""
    Who: Ericson Mattoso
    When: 04/nov/2021
    What: This script is responsable to take info from all houses in pararius.
    Why: Need this info to display on my app
    Where: pararius.nl
    How: scrapping data through selenium and BeautifulSoup
"""
# import libs
from bs4 import BeautifulSoup
from datetime import date
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd

# getting today date
today = date.today()

def scrape_web(url):
    """
        the purpose of the function is to scrape a page
        it creates fake browser to do not getting blocked
        then it transform the html into a string value
    """
    # open options to add specifications
    chrome_options = Options()
    # add size of the browser to be invisible
    chrome_options.add_argument("--window-size=%s" % "1,1")
    # reads the chromedriver file with the options openning the browser
    driver = webdriver.Chrome(
        'temp/chromedriver', chrome_options=chrome_options)
    # set a position to make the new browser be invisible
    driver.set_window_position(-10000, 0)
    # request the url status
    driver.get(url)
    # transforms selenium to Beautiful Soup
    html_soup = BeautifulSoup(driver.page_source)
    # after getting the needed info, close browser
    driver.close()
    # return html page
    return html_soup


# url to scrape
url = 'https://www.pararius.com/apartments/nederland/page-'

# If the page block the bot here it will try another User-Agent
num_pages = None

# run the scrape, if it finds a value it update the variable and skip the while condition
html_soup = scrape_web(url+'1')

# how many pages
num_pages = html_soup.find_all('a', {"class": "pagination__link"})[4].text

# Save number of pages and number of adds
num_rents = html_soup.find_all('div', {"class": "pagination__summary"})[0].text
num_rents = int(num_rents.split()[-2])
num_pages = int(num_pages)
print(num_rents)
print(num_pages)

# variable
houses = []

# Here it will go in each page and save all adds into a variable
for count in range(1, num_pages+1):
    # flag
    print(">>>>>>>>>", count)

    while validator is None:
        # scraper
        html_soup = scrape_web((url + str(count)))
        # didn't find a content, so it will run the scrape with another agent
        validator = 'Not Null'
        # get all ads
        house_data = html_soup.find_all(
            'li', class_="search-list__item search-list__item--listing")
        # save ads in a list
        houses.append(house_data)
        print('saved')

# variables
price_ = []
address_ = []
street_ = []
agency_ = []
irl_ = []
image_ = []
description_2 = []

# go to each page
for n_pages in range(num_pages):
    # how many houses we have in this page?
    n_pages_len = len(houses[n_pages])
    # going to each add of a bunch in a page
    for n_rents in range(n_pages_len):
        # soup to add
        num = (houses[n_pages][n_rents])
        # features of the house
        list_li = num.find_all('li', {"class": "illustrated-features__item"})

        try:
            # house is free or under option
            p5_value = num.find_all(
                'span', {"class": "listing-label listing-label--under-option"})[0].text
        except:
            # house is free or under option
            p5_value = None

        # dict
        description_1 = {}

        # features of the house should be a list because there are many possibilities
        for i in range(len(list_li)):
            # key
            a = (list_li[i]["class"][1][28:])
            # value
            b = (list_li[i].text)

            # save features into a dict
            description_1.update({
                a: b,
                'status': p5_value,
            })
        # get small dit and save as list to future df
        description_2.append(description_1)

        # get price of the ad
        price = num.find_all(
            'div', {"class": "listing-search-item__price"})[0].text
        price_.append(price)

        # gets location on the ad
        address = num.find(
            'div', {"class": "listing-search-item__location"}).text
        address_.append(address)

        # gets title of the ad
        street = num.find_all(
            'a', {"class": "listing-search-item__link listing-search-item__link--title"})[0].text
        street_.append(street)

        # gets the link to the post
        irl = num.find_all('a', {
                           "class": "listing-search-item__link listing-search-item__link--title"})[0]['href']
        irl_.append(irl)

        # gets link to the img
        image = num.find_all('img')[0]['src']
        image_.append(image)

        # gets agency name
        agency = num.find_all('a', href=True)[2].text
        agency_.append(agency)

#  transforming dict into dataframe
df_pararius_1 = pd.DataFrame({
    'price': price_,
    'address': address_,
    'street': street_,
    'agency': agency_,
    'irl': irl_,
    'image': image_,
})

# transforming dict into dataframe
df_pararius_2 = pd.DataFrame(description_2)


# transforming all files into only one
df_pararius = pd.concat([df_pararius_1, df_pararius_2], 1)
df_pararius.to_csv(f'../data/processed/df_pararius.csv')

# removing unwanted char
df_pararius['surface-area'] = df_pararius['surface-area'].str.replace(
    "\D", "", regex=True)

# removing unwanted char
df_pararius['number-of-rooms'] = df_pararius['number-of-rooms'].str.replace(
    "\D", "", regex=True)

# removing unwanted char
df_pararius['garden-surface-area'] = df_pararius['garden-surface-area'].str.replace(
    "\D", "", regex=True)

# removing unwanted char
df_pararius['plot-size'] = df_pararius['plot-size'].str.replace(
    "\D", "", regex=True)

# creating index
df_pararius = df_pararius.dropna(axis=1, how='all')

# removing unwanted char
df_pararius['price'] = df_pararius['price'].str.replace("\D", "", regex=True)

# removing unwanted char
df_pararius['address'] = df_pararius['address'].str.replace(
    '\n|new|  ', "", regex=True)

# get the postcode
df_pararius['postcode'] = df_pararius['address'].str.replace(
    "\s", "", regex=True).str[0:6]

# when the file was produced
df_pararius['date'] = str(today)

# removing unwanted char
df_pararius['status'] = df_pararius['status'].str.replace('\n', "", regex=True)

# if we have duplicate, remove it
df_pararius = df_pararius.drop_duplicates(
    subset=['irl']).reset_index(drop=True)

# create name of the file
today_csv = ("df_pararius_" + str(today)+'.csv')

# save the scrape material
df_pararius.to_csv(f'../data/temp/{today_csv}')
