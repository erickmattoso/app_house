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
from datetime import date
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import datetime
import glob
import os
import pandas as pd
import time


def scrape(city, num_pages):
    driver = webdriver.Chrome(chromedriver)
    url = f'https://www.pararius.com/apartments/{city}/page-{num_pages}'
    driver.get(url)
    time.sleep(5)
    html_soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.close()
    return html_soup


chromedriver = ChromeDriverManager().install()

my_links_list = []
my_list = ["alkmaar", "almere", "amersfoort", "amstelveen", "amsterdam", "apeldoorn", "arnhem", "breda", "bussum", "delft", "dordrecht", "eindhoven", "gouda", "haarlem",
           "hilversum", "hoofddorp", "huizen", "leiden", "oegstgeest", "rijswijk", "rotterdam", "schiedam", "utrecht", "voorburg", "zaandam", "zeist", "zoetermeer", "den-bosch", "den-haag"]
my_list.sort()
for city in (my_list[:]):
    html_soup = scrape(city, 1)
    try:
        num_pages = int(html_soup.find_all(
            'a', {"class": "pagination__link"})[0].text)
    except:
        num_pages = 1
    my_links = html_soup.find_all(
        'a', {"class": "listing-search-item__link listing-search-item__link--depiction"})
    my_links_list.append(my_links)
    if num_pages > 1:
        for i in range(2, num_pages+1):
            html_soup = scrape(city, num_pages)

my_csv = []
result = [item for sublist in my_links_list for item in sublist]
for i in range(len(result)):
    my_csv.append(result[i]['href'])

# contém tudo ativo
acti = pd.DataFrame(my_csv, columns={"links"})

# base antiga
base = pd.read_csv('../data/processed/all_content.csv', index_col=[0])

# transformando em lista para comparar
acti_list = list(acti['links'])
base_list = list(base['link'])

# O que tem de novo?
crawler = set(acti_list) - set(base_list)

# Salva a base atual como base final
acti.to_csv('../data/processed/my_links.csv')

# Salva onde o crawler deve buscar novas infos
df_crawler = pd.DataFrame(crawler, columns={"links"})
df_crawler.to_csv('../data/processed/df_crawler.csv')

print(len(crawler))


def scrape(my_link):
    driver = webdriver.Chrome(chromedriver)
    url = f'https://www.pararius.com{my_link}'
    driver.get(url)
    time.sleep(5)
    html_soup = BeautifulSoup(driver.page_source, 'html.parser')
    return html_soup, driver


def content_table(table):
    content = html_soup.find_all(
        'section', class_=f"page__details page__details--{table}")[0]
    content_title = content.find_all('dt')
    content_cores = content.find_all('dd')
    return content_title, content_cores


def del_files():
    files = glob.glob('../data/temp/*')
    for f in files:
        os.remove(f)


chromedriver = ChromeDriverManager().install()

del_files()

for my_link in list(df_crawler['links'])[:]:
    transfer_title_list = []
    transfer_cores_list = []
    dimensions_title_list = []
    dimensions_cores_list = []
    construction_title_list = []
    construction_cores_list = []
    layout_title_list = []
    layout_cores_list = []
    outdoor_title_list = []
    outdoor_cores_list = []
    energy_title_list = []
    energy_cores_list = []
    parking_title_list = []
    parking_cores_list = []
    garage_title_list = []
    garage_cores_list = []

    html_soup, driver = scrape(my_link)

    try:
        title = html_soup.find_all(
            'h1', class_="listing-detail-summary__title")[0].text
        location = html_soup.find_all(
            'div', class_="listing-detail-summary__location")[0].text
        price = html_soup.find_all(
            'div', class_="listing-detail-summary__price")[0].text
        img = html_soup.find_all('img', class_="picture__image")[0]['src']
        #########################################################################
        try:
            transfer_title, transfer_cores = content_table("transfer")
            for i in range(len(transfer_title)):
                transfer_title_list.append('transfer '+transfer_title[i].text)
                transfer_cores_list.append(transfer_cores[i].text)
        except:
            transfer_title_list.append('')
            transfer_cores_list.append('')
        #########################################################################
        try:
            dimensions_title, dimensions_cores = content_table("dimensions")
            for i in range(len(dimensions_title)):
                dimensions_title_list.append(
                    'dimensions '+dimensions_title[i].text)
                dimensions_cores_list.append(dimensions_cores[i].text)
        except:
            dimensions_title_list.append('')
            dimensions_cores_list.append('')
        #########################################################################
        try:
            construction_title, construction_cores = content_table(
                "construction")
            for i in range(len(construction_title)):
                construction_title_list.append(
                    'construction '+construction_title[i].text)
                construction_cores_list.append(construction_cores[i].text)
        except:
            construction_title_list.append('')
            construction_cores_list.append('')
        #########################################################################
        try:
            layout_title, layout_cores = content_table("layout")
            for i in range(len(layout_title)):
                layout_title_list.append('layout '+layout_title[i].text)
                layout_cores_list.append(layout_cores[i].text)
        except:
            layout_title_list.append('')
            layout_cores_list.append('')
        #########################################################################
        try:
            outdoor_title, outdoor_cores = content_table("outdoor")
            for i in range(len(outdoor_title)):
                outdoor_title_list.append('outdoor '+outdoor_title[i].text)
                outdoor_cores_list.append(outdoor_cores[i].text)
        except:
            outdoor_title_list.append('')
            outdoor_cores_list.append('')
        #########################################################################
        try:
            energy_title, energy_cores = content_table("energy")
            for i in range(len(energy_title)):
                energy_title_list.append('energy '+energy_title[i].text)
                energy_cores_list.append(energy_cores[i].text)
        except:
            energy_title_list.append('')
            energy_cores_list.append('')
        #########################################################################
        try:
            parking_title, parking_cores = content_table("parking")
            for i in range(len(parking_title)):
                parking_title_list.append('parking '+parking_title[i].text)
                parking_cores_list.append(parking_cores[i].text)
        except:
            parking_title_list.append('')
            parking_cores_list.append('')
        #########################################################################
        try:
            garage_title, garage_cores = content_table("garage")
            for i in range(len(garage_title)):
                garage_title_list.append('garage '+garage_title[i].text)
                garage_cores_list.append(garage_cores[i].text)
        except:
            garage_title_list.append('')
            garage_cores_list.append('')
        #########################################################################

        df1 = pd.DataFrame([transfer_cores_list],
                           columns=[transfer_title_list])
        df2 = pd.DataFrame([dimensions_cores_list],
                           columns=[dimensions_title_list])
        df3 = pd.DataFrame([construction_cores_list],
                           columns=[construction_title_list])
        df4 = pd.DataFrame([layout_cores_list], columns=[layout_title_list])
        df5 = pd.DataFrame([outdoor_cores_list], columns=[outdoor_title_list])
        df6 = pd.DataFrame([energy_cores_list], columns=[energy_title_list])
        df7 = pd.DataFrame([parking_cores_list], columns=[parking_title_list])
        df8 = pd.DataFrame([garage_cores_list], columns=[garage_title_list])

        df_title = pd.DataFrame([title], columns=["title"])
        df_location = pd.DataFrame([location], columns=["location"])
        df_price = pd.DataFrame([price], columns=["price"])
        df_link = pd.DataFrame([my_link], columns=["link"])
        df_img = pd.DataFrame([img], columns=["img"])

        df = pd.concat([df_title, df_location, df_price, df_link,
                       df_img, df1, df2, df3, df4, df5, df6, df7, df8], 1)

        file_name = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S_%s")
        df.to_csv(f'../data/temp/my_links_{file_name}.csv')
        driver.close()
    except:
        print(my_link)
        driver.close()
        pass

files = os.path.join("../data/temp", "my_links*.csv")
files = glob.glob(files)
df = pd.concat(map(pd.read_csv, files), ignore_index=True)
df = df.loc[:, ~df.columns.str.startswith("('',)")]

col = df.columns
col = [word.replace("'", '') for word in col]
col = [word.replace(",", '') for word in col]
col = [word.replace("(", '') for word in col]
col = [word.replace(")", '') for word in col]
col = (map(lambda x: x.lower(), col))
col = list(col)
df.columns = col

base = pd.read_csv('../data/processed/all_content.csv', index_col=[0])
DS = pd.concat([df, base], ignore_index=True)

DS = DS[DS['link'].isin(list(acti['links']))]

DS = DS.reset_index(drop=True)
DS.to_csv('../data/processed/all_content.csv')
del_files()
os.remove('../data/processed/df_crawler.csv')
os.remove('../data/processed/my_links.csv')
