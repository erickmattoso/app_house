#!/usr/bin/env python
# coding: utf-8

# # Objective

# Here we will scrape infos of dates do `Availability` and `Offered Since` of each new page in our database.

# # Libs

# In[1]:


# # Import Libs
# from bs4 import BeautifulSoup
# from datetime import date
# from datetime import datetime, timedelta
# from folium.plugins import FastMarkerCluster
# from requests import get
# import datetime
# import datetime as dt
# import folium
# import pandas as pd
# import streamlit as st
# today = date.today()


# In[2]:


import requests
from fake_useragent import UserAgent
import time
from bs4 import BeautifulSoup
from datetime import date
import requests
from requests import get
import pandas as pd
today = date.today()


# # Imports

# In[3]:


df_pararius = pd.read_csv('app/df_coo_pararius.csv',index_col=[0])
house_temp  = pd.read_csv('data/processed/house_temp.csv',index_col=[0])


# # What is new?
# Here we will scrape infos of dates do `Availability` and `Offered Since` of each new page in our database.

# In[4]:


temp1 = df_pararius['url'].unique()
temp2 = house_temp['url'].unique()
urls = list(set(temp1) - set(temp2))
print(len(urls))


# # Get data from table

# Going in each page, I want to scrape tables to get specific dates

# In[5]:


def key_val(text):
    part = html_soup.find("dt",text=text)
    key = (part.text.strip())
    val = (part.findNext("dd").text.strip())
    return key, val


# Getting data and saving in a variable

# In[6]:


def scrape_web(url):    
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    ua=UserAgent()
    hdr = {'User-Agent': ua.random,
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
          'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
          'Accept-Encoding': 'none',
          'Accept-Language': 'en-US,en;q=0.8',
          'Connection': 'keep-alive'}
    time.sleep(2)
    response = requests.get(url, headers=hdr)
    time.sleep(4)
    html_soup = BeautifulSoup(response.content,"lxml")   
    return html_soup


# In[7]:


not_available=[]
description_2=[]

for url in urls:
    description_1={}
    html_soup = scrape_web(url)

    try:
        key1, val1 = key_val("Offered since")
        key2, val2 = key_val("Available")
        description_1.update({
            'url':url,
            key1:val1,
            key2:val2,
        })
        description_2.append(description_1)
        # print(key1, val1)
        # print(key2, val2)
    except:
        pass


# # Add dates into original dataframe

# In[8]:


house_temp_ = pd.DataFrame(description_2)
house_temp = pd.concat([house_temp, house_temp_],0)


# # Transform date str into Date Time

# function to transform data

# In[9]:


def fixing_time_delta(df, time, my_ofset):
    fixing_time_delta = df.loc[df['Offered since'].str.contains(time, na=False), 'Offered since']
    fixing_time_delta = fixing_time_delta.str.replace("\D","",regex=True).astype(int)
    fixing_time_delta = today - fixing_time_delta.apply(my_ofset)
    fixing_time_delta = pd.to_datetime(fixing_time_delta).dt.strftime('%d-%m-%Y')
    df.loc[df['Offered since'].str.contains(time, na=False), 'Offered since'] = fixing_time_delta
    return df


# appling function

# In[10]:


try:
    house_temp = fixing_time_delta(house_temp,"week",pd.offsets.Week)
    house_temp = fixing_time_delta(house_temp,"month",pd.offsets.MonthBegin)
except:
    print('erro')
    pass


# In[11]:


today = date.today()
house_temp['Available'] = house_temp['Available'].str.replace("From","")
house_temp['Available'] = house_temp['Available'].str.replace("Immediately|In consultation",str(today))
house_temp['Available'] = pd.to_datetime(house_temp['Available']).dt.strftime('%d-%m-%Y')


# # Save house_temp

# In[12]:


house_temp = house_temp.drop_duplicates(subset=['url']).reset_index(drop=True)


# In[13]:


house_temp.to_csv('data/processed/house_temp.csv')


# # Add house temp into df_pararius

# In[14]:


result = pd.merge(df_pararius, house_temp, how='left', on='url')


# In[15]:


#result['Offered since'] = pd.to_datetime(result['Offered since'], format='%d-%m-%Y')


# # Save whole DataFrame

# In[16]:


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


# In[17]:


result2 = result2.rename(columns={
    'img': 'Add',
    'price': 'Price',
    'Plaats': 'City',
    'surface-area': 'Area',
    'number-of-rooms': 'Rooms',
    'garden-surface-area': 'Garden',
    'Offered since': 'Offered',
    'Available': 'Available',})


# In[18]:


result2.to_csv('app/df_coo_pararius2.csv')


# In[ ]:




