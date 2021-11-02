import requests
from fake_useragent import UserAgent
import time
from bs4 import BeautifulSoup
from datetime import date
import requests
from requests import get
import pandas as pd
today = date.today()


def scrape_web(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    ua = UserAgent()
    hdr = {'User-Agent': ua.random,
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
           'Accept-Encoding': 'none',
           'Accept-Language': 'en-US,en;q=0.8',
           'Connection': 'keep-alive'}
    time.sleep(2)
    response = requests.get(url, headers=hdr)
    time.sleep(4)
    html_soup = BeautifulSoup(response.content, "lxml")
    return html_soup


url = 'https://www.pararius.com/apartments/nederland/page-'
html_soup = scrape_web(url+'1')
num_pages = html_soup.find_all('a', {"class": "pagination__link"})[4].text
num_pages = int(num_pages)
num_rents = html_soup.find_all('div', {"class": "pagination__summary"})[0].text
num_rents = int(num_rents.split()[-2])
houses = []
for count in range(1, num_pages+1):
    try:
        html_soup = scrape_web(url + str(count))
        house_data = html_soup.find_all(
            'li', class_="search-list__item search-list__item--listing")
        houses.append(house_data)
    except:
        pass

price_ = []
address_ = []
street_ = []
agency_ = []
irl_ = []
image_ = []
description_2 = []

for n_pages in range(num_pages):
    n_pages_len = len(houses[n_pages])
    for n_rents in range(n_pages_len):
        num = (houses[n_pages][n_rents])
        list_li = num.find_all('li', {"class": "illustrated-features__item"})
        description_1 = {}

        try:
            p5_value = num.find_all(
                'span', {"class": "listing-label listing-label--under-option"})[0].text
        except:
            p5_value = None

        for i in range(len(list_li)):
            a = (list_li[i]["class"][1][28:])
            b = (list_li[i].text)
            description_1.update({
                a: b,
                'status': p5_value,
            })
        description_2.append(description_1)

        price = num.find_all(
            'div', {"class": "listing-search-item__price"})[0].text
        price_.append(price)
        address = num.find(
            'div', {"class": "listing-search-item__location"}).text
        address_.append(address)
        street = num.find_all(
            'a', {"class": "listing-search-item__link listing-search-item__link--title"})[0].text
        street_.append(street)
        irl = num.find_all('a', {
                           "class": "listing-search-item__link listing-search-item__link--title"})[0]['href']
        irl_.append(irl)
        image = num.find_all('img')[0]['src']
        image_.append(image)
        agency = num.find_all('a', href=True)[2].text
        agency_.append(agency)

df_pararius_1 = pd.DataFrame({
    'price': price_,
    'address': address_,
    'street': street_,
    'agency': agency_,
    'irl': irl_,
    'image': image_,
})

df_pararius_2 = pd.DataFrame(description_2)
df_pararius = pd.concat([df_pararius_1, df_pararius_2], 1)
df_pararius['surface-area'] = df_pararius['surface-area'].str.replace(
    "\D", "", regex=True)
df_pararius['number-of-rooms'] = df_pararius['number-of-rooms'].str.replace(
    "\D", "", regex=True)
df_pararius['garden-surface-area'] = df_pararius['garden-surface-area'].str.replace(
    "\D", "", regex=True)
df_pararius['plot-size'] = df_pararius['plot-size'].str.replace(
    "\D", "", regex=True)
df_pararius = df_pararius.dropna(axis=1, how='all')
df_pararius['price'] = df_pararius['price'].str.replace("\D", "", regex=True)
df_pararius['address'] = df_pararius['address'].str.replace(
    '\n|new|  ', "", regex=True)
df_pararius['postcode'] = df_pararius['address'].str.replace(
    "\s", "", regex=True).str[0:6]
df_pararius['date'] = str(today)
df_pararius['status'] = df_pararius['status'].str.replace('\n', "", regex=True)
df_pararius = df_pararius.drop_duplicates(
    subset=['irl']).reset_index(drop=True)
today_csv = ("df_pararius_" + str(today)+'.csv')
df_pararius.to_csv(f'data/temp/{today_csv}')
# df_pararius.to_csv(f'data/temp/test.csv')
