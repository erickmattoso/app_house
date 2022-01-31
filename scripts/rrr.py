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
url = 'https://www.funda.nl/en/huur/voorburg/p'

# run the scrape, if it finds a value it update the variable and skip the while condition
html_soup = scrape_web(url+'1')

# how many pages
# num_pages = html_soup.find_all('a', {"class": "pagination__link"})[4].text
num_rents = html_soup.find_all(
    'h1', {"class": "search-output-result-count fd-m-none fd-m-bottom-s fd-flex fd-flex-column"})[0].text
num_rents = int(num_rents.split()[0])
print(num_rents)
num_pages = 3

# variable
houses = []

# Here it will go in each page and save all adds into a variable
for count in range(1, num_pages+1):

    # flag
    print(">>>>>>>>>", count)

    # scraper
    html_soup = scrape_web((url + str(count)))

    # get all ads
    # house_data = html_soup.find_all('ol', class_="search-results")

    # save ads in a list
    houses.append(html_soup)

# variables
price_ = []
address_ = []
street_ = []
agency_ = []
irl_ = []
image_ = []

# go to each page
for n_pages in range(num_pages):
    # how many houses we have in this page?
    n_pages_len = len(houses[n_pages])
    print("how many houses we have in this page?", n_pages_len)
    # going to each add of a bunch in a page
    for n_rents in range(n_pages_len):
        # soup to add
        num = (houses[n_pages][n_rents])

        # get price of the ad
        price = num.find_all('span', {"class": "search-result-price"})[0].text
        print(price)
        price_.append(price)

        # gets location on the ad
        address = num.find_all(
            'h4', {"class": "search-result__header-subtitle fd-m-none"})[0].text
        address_.append(address)

        # gets title of the ad
        street = num.find_all(
            'h2', {"class": "search-result__header-title fd-m-none"})[0].text
        street_.append(street)

        # gets the link to the post
        irl = num.find_all(
            'a', {"data-object-url-tracking": "resultlist"})[0]['href']
        irl_.append(irl)

        # gets link to the img
        image_alias = html_soup.find('div', {"class": "search-result-image"})
        image = image_alias.find('img').attrs['src']
        print(image)
        image_.append(image)

        # gets agency name
        agency = num.find_all(
            'span', {"class": "search-result-makelaar-name"})[0].text
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

df_pararius_1.to_csv(f'test.csv')
print(df_pararius_1.shape)
df_pararius_1
