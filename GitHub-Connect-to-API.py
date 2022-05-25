import requests
from pprint import pprint
from prettytable import PrettyTable
from bs4 import BeautifulSoup
import json
import re
import GitHubKey
from time import sleep
import csv
import pandas as pd
import numpy as np

def get_organisations():
    #put in your token from GitHub in order to access the APi
    #key = ''
    headers = {'Authorization': f'token {GitHubKey.key}'}
    query_url = 'https://api.github.com/search/code'
    html_list = []
    #iterates through the list of organisations and finds the html_url
    n = 1
    with open('organisations.txt') as f:
        for line in f:
            sleep(60)
            organisation = line.strip()
            params = {
                'q': f'openapi org:{organisation}'
            }
            #Input search parameters to look for 'openapi' within the organisations
            r = requests.get(query_url, headers=headers, params=params)
            if n % 25 ==0:
                sleep(180)
            n += 1
            print(n)
            response = r.json()
            pprint(r.headers)
            print(response)
            items = response['items']
            #returns the html url from the API request and populates a list
            for x in items:
                html_urls = x['html_url']
                html_list.append(html_urls)
    #saves as a Pandas series
    df = pd.Series(html_list, dtype=str)
    #saves output as html_paths for speed in order to avoid running both
    np.savetxt("html_paths.txt", df.values, fmt='%s')




#iterates through the list and looks for openapi:
    openapilist = []
    for html in html_list:
        r2 = requests.get(html).content
        soup = BeautifulSoup(r2, 'html.parser')
        results = soup.find_all(class_="blob-code blob-code-inner js-file-line")
        print(results)
        #if results is not None:
        for x in results:
            if 'openapi:' in x.text:
                openapilist.append(html)
    df2 = pd.Series(openapilist, dtype=str)
    #need to delete the 0 from the top of the outputted csv
    df2.to_csv("outputforlinter.csv", sep=',', index=False)

if __name__ == '__main__':
    get_organisations()


"""
#alternative that runs off an already scraped list of html paths for speed
def get_organisations():
    openapilist = []
    with open('html_paths.txt', newline='') as f:
        for htmlpaths in f:
            htmlpaths = htmlpaths.strip()
            print(htmlpaths)
            r2 = requests.get(htmlpaths).content
            #pprint(r2)
            soup = BeautifulSoup(r2, 'html.parser')
            results = soup.find_all(class_="blob-code blob-code-inner js-file-line")
            print(results)
            #if results is not None:
            for x in results:
                #print(x)
                if 'openapi:' in x.text:
                    print(x.text)
                    print(htmlpaths)
                    openapilist.append(htmlpaths)
    df = pd.Series(openapilist, dtype=str)
    df.to_csv("output.txt", header=None, index=None, sep='', mode='a')


if __name__ == '__main__':
    get_organisations()
"""


