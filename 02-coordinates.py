#!/usr/bin/env python
# coding: utf-8

# # libs

# In[1]:


from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim
from scipy import spatial
import glob
import os
import pandas as pd
import requests


# # Data

# ## df pararius

# In[2]:


list_of_files = glob.glob("data/temp/df_pararius_*.csv") # * means all if need specific format then *.csv
latest_file = max(list_of_files, key=os.path.getctime)
df_pararius = pd.read_csv(latest_file, index_col=[0])


# ## zipcodeZ

# In[3]:


df_zipcode = pd.read_csv('data/processed/zipcodeZ.csv',index_col=[0])


# # What is new?
# These are new postcodes that we do not have in our database

# In[4]:


temp1 = df_pararius['postcode'].unique()
temp2 = df_zipcode['postcode'].unique()
cep_zip = list(set(temp1) - set(temp2))
print(len(cep_zip))


# ## crawler
# get data from "postcode bij adres"

# In[5]:


def html_content(cep):
    url = 'https://postcodebijadres.nl/' + cep
    headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0"}
    soup = BeautifulSoup(requests.get(url, headers=headers).content, "html.parser")
    return soup


# In[6]:


zipcode=pd.DataFrame({})
description_1={}

for cep in cep_zip:
    soup = html_content(cep)
    
    try:
        
        for num in range(9):
            
            split0 = soup.find_all('table',{"class":"table table-bordered mt-3"})[0]
            split1 = soup.find_all('table',{"class":"table table-bordered mt-3"})[1]
            
            split0_key = split0.find_all('th')[num].text
            split0_val = split0.find_all('td')[num].text

            lat = split1.find_all('td')[1].text
            lon = split1.find_all('td')[3].text
                                   
            description_1.update({
                split0_key:split0_val,
                'latitude':lat,
                'longitude':lon
            })


        zipcode_ = pd.DataFrame(description_1,index=[0])
        zipcode  = pd.concat([zipcode,zipcode_],0)
        
        
        zipcode.to_csv(f'data/temp/cep/zipcode_{cep}.csv')
        print(cep)
    except:
        
        print('#####################################',cep)
        pass


# ## cleaning data and save

# In[7]:


try:
    zipcode['Straat'] = zipcode['Straat'].str.replace('\n',"",regex=True)
    zipcode['Postcode'] = zipcode['Postcode'].str.replace(' ',"",regex=True)
    zipcode = zipcode.rename(columns={'Postcode':'postcode'})
    zipcode = pd.concat([zipcode,df_zipcode],0).reset_index(drop=True)
    zipcode = zipcode.drop_duplicates(subset=['postcode']).reset_index(drop=True)
except:
    zipcode = df_zipcode.copy()


# In[8]:


zipcode_pararius_coo = pd.merge(df_pararius, zipcode, how='left',on='postcode')


# # organizing before saving

# In[9]:


zipcode_pararius_coo = zipcode_pararius_coo.fillna(0).drop_duplicates(subset=['irl']).reset_index(drop=True)


# In[10]:


zipcode_pararius_coo.loc[zipcode_pararius_coo['interior']==0, 'interior'] = 'Upholstered'
zipcode_pararius_coo.loc[zipcode_pararius_coo['status']==0, 'status'] = 'Free'


# In[11]:


# zipcode_pararius_coo['city'] = zipcode_pararius_coo['irl'].str.split("/",expand=True)[2].str.replace("-", " ").str.title()


# In[12]:


# prepare link on streamlit
zipcode_pararius_coo['url'] = 'https://www.pararius.com' + zipcode_pararius_coo['irl']
zipcode_pararius_coo['link'] = "<a target='_blank' href=" + (zipcode_pararius_coo['url']).astype(str) + ">" + (zipcode_pararius_coo['street']).astype(str) + "</a>"
zipcode_pararius_coo['img'] = "<a href=" + zipcode_pararius_coo['url'] + " target='blank'><img src=" + zipcode_pararius_coo['image'] + " title='rent' width='150' height='100'/></a>"


# # save data

# In[13]:


zipcode_pararius_coo.to_csv('app/df_coo_pararius.csv')


# In[14]:


zipcode.to_csv('data/processed/zipcodeZ.csv')

