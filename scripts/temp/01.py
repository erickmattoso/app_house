# import libs
from bs4 import BeautifulSoup
from datetime import date
from fake_useragent import UserAgent
import pandas as pd
import requests
import time

# getting today date
today = date.today()


def scrape_web(url):
    """
        the purpose of the function is to scrape a page
        it creates fake browser to do not getting blocked
        then it transform the html into a string value
    """

    # UserAgent() creates the random User-Agent
    ua = UserAgent()
    hdr_ua = ua.random
    hdr = {
        'User-Agent': hdr_ua,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive'}

    # give some sleep before accessing in order to reproduce a human behavior
    time.sleep(2.5)

    # get the status response
    response = requests.get(url, headers=hdr)

    # give some sleep before accessing in order to reproduce a human behavior
    time.sleep(2.5)

    # get the page content
    html_soup = BeautifulSoup(response.content, "lxml")

    # return content as string
    return html_soup, hdr


# url to scrape
url = 'https://www.pararius.com/apartments/nederland/page-'

# If the page block the bot here it will try another User-Agent
num_pages = None

hdr_list = []
hdr_list_e = []
while num_pages is None:
    try:
        # run the scrape, if it finds a value it update the variable and skip the while condition
        html_soup, hdr = scrape_web(url+'1')
        # print(hdr)
        num_pages = html_soup.find_all(
            'a', {"class": "pagination__link"})[4].text
        hdr_list.append(hdr)
    except:
        # didn't find a content, so it will run the scrape with another agent
        hdr_list_e.append(hdr)
        pass

# Save number of pages and number of adds
num_rents = html_soup.find_all('div', {"class": "pagination__summary"})[0].text
num_rents = int(num_rents.split()[-2])
num_pages = int(num_pages)
# num_pages = 5

# variable
houses = []

# Here it will go in each page and save all adds into a variable
for count in range(1, num_pages+1):
    # flag
    validator = None
    print(">>>>>>>>>", count)

    while validator is None:
        # scraper
        html_soup, hdr = scrape_web((url + str(count)))
        # print(hdr)
        try:
            # run the scrape, if it finds a value it update the variable and skip the while condition
            print(html_soup.find_all('p', {"class": "header"})[0].text.strip())
            hdr_list_e.append(hdr)
        except:
            # didn't find a content, so it will run the scrape with another agent
            validator = 'Not Null'
            # get all ads
            house_data = html_soup.find_all(
                'li', class_="search-list__item search-list__item--listing")
            # save ads in a list
            houses.append(house_data)
            hdr_list.append(hdr)
            print('saved')

# variables
price_ = []
address_ = []
street_ = []
agency_ = []
irl_ = []
image_ = []
description_2 = []

# Lorem
for n_pages in range(num_pages):
    # Lorem
    n_pages_len = len(houses[n_pages])

    # Lorem
    for n_rents in range(n_pages_len):

        # Lorem
        num = (houses[n_pages][n_rents])

        # Lorem
        list_li = num.find_all('li', {"class": "illustrated-features__item"})

        # Lorem
        description_1 = {}

        try:
            # Lorem
            p5_value = num.find_all(
                'span', {"class": "listing-label listing-label--under-option"})[0].text
        except:
            # Lorem
            p5_value = None

        # Lorem
        for i in range(len(list_li)):
            # Lorem
            a = (list_li[i]["class"][1][28:])
            # Lorem
            b = (list_li[i].text)

            # Lorem
            description_1.update({
                a: b,
                'status': p5_value,
            })
        # Lorem
        description_2.append(description_1)

        # Lorem
        price = num.find_all(
            'div', {"class": "listing-search-item__price"})[0].text
        price_.append(price)

        # Lorem
        address = num.find(
            'div', {"class": "listing-search-item__location"}).text
        address_.append(address)

        # Lorem
        street = num.find_all(
            'a', {"class": "listing-search-item__link listing-search-item__link--title"})[0].text
        street_.append(street)

        # Lorem
        irl = num.find_all('a', {
                           "class": "listing-search-item__link listing-search-item__link--title"})[0]['href']
        irl_.append(irl)

        # Lorem
        image = num.find_all('img')[0]['src']
        image_.append(image)

        # Lorem
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

# save headers files
pd.DataFrame(hdr_list).to_csv(f'../data/processed/headers.csv')
pd.DataFrame(hdr_list_e).to_csv(f'../data/processed/headers_e.csv')
