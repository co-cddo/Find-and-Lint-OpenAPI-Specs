import pandas as pd
import urllib
import os
from bs4 import BeautifulSoup
import re
from datetime import date
import requests
import json

#creates a list of htmls to parse through
def create_htmlpaths(path):
    htmlpaths = []

    for filename in os.listdir(input_path):
        if filename.endswith("html"):
            htmlpaths.append(input_path + filename)
    return htmlpaths


def create_url(htmlpath):
    with open(htmlpath) as rawhtml:
        soup = BeautifulSoup(rawhtml, "html.parser")
        body = soup.find_all('td')
        url = soup.find_all('th')
        htmlbody = [x.text for x in body]
        urlfind = [x.text for x in url]
        urlfind = [x.strip() for x in urlfind]
        urlonly = re.search("(?P<url>https?://[^\s]+)", str(urlfind)).group("url")
        urlonly = urlonly.replace(r'\n', '')
    return urlonly


# if checksjsoninurl function says it has found json
def withjsoninurl(url):
    r2 = requests.get(url).json()
    if 'openapi' in r2:
        version = r2['openapi']
    else:
        version = 'Not found'
    if 'info' in r2:
        if 'title' in r2['info']:
            title = r2['info']['title']
        else:
            title = 'Not found'
    else:
        title = 'Not found'

    return title, version


# if checksjsoninurl function says it hasn't found json
def nojsoninurl(url):
    r2 = requests.get(url).content
    soup = BeautifulSoup(r2, 'html.parser')
    if soup.string is not None:
        title = soup.string.split()
    else:
        title = []

    if title.count("openapi:") >= 1:
        index = title.index("openapi:")
        version = title[index + 1]
    elif title.count("Openapi:") >= 1:
        index = title.index("Openapi:")
        version = title[index + 1]
    else:
        version = 'Not found'

    if title.count("title:") >= 1:
        findtitle = title.index("title:")
        title = title[findtitle + 1]
    elif title.count("Title:") >= 1:
        findtitle = title.index("Title:")
        title = title[findtitle + 1]
    else:
        title = 'Not found'

    return title, version


# calls and runs 1 url through withjsoninurl function and nojsoninurl function depending on if statements
def checksjsoninurl(url):
    if 'json' not in url:
        title, version = nojsoninurl(url)
    elif 'json' in url:
        title, version = withjsoninurl(url)

    return title, version

#creates a dataframe
def create_dataframe(htmlpath):
    with open(htmlpath) as rawhtml:
        soup = BeautifulSoup(rawhtml, "html.parser")
        body = soup.find_all('td')
        body = [x.text for x in body]
        html_df = pd.DataFrame(
            {'Location of warning or error': body[0::3],
             'Warning or Error': body[1::3],
             'Information about the warning or error': body[2::3],
             })
        urlonly = create_url(htmlpath)
        slashparts = str(urlonly).split('/')
        organisation = '/'.join(slashparts[3:4])
        description = '/'.join(slashparts[4:5])
        html_df['Raw URL'] = urlonly
        html_df['Organisation'] = organisation.lower()
        html_df['Description'] = description
        title, version = checksjsoninurl(urlonly)
        version = str(version).replace('"', '').replace("'", '')
        html_df['API Version'] = version
        html_df['Title'] = str(title).strip()
        today = pd.to_datetime("today").strftime("%m/%d/%Y")
        html_df['Date of Creation'] = today
        html_df['Warning Total per Row'] = html_df['Warning or Error'].apply(lambda x: '1' if x == 'warning' else '0')
        html_df['Error Total per Row'] = html_df['Warning or Error'].apply(lambda x: '1' if x == 'error' else '0')

    return html_df


def createwarningstab(dataframe):
    warningsdf = dataframe.groupby(['Information about the warning or error', 'Warning or Error']).count().sort_values(
        by='URL').reset_index()
    warningsdf = warningsdf[['Information about the warning or error', 'Warning or Error', 'URL']]
    warningsdf.columns = ['Information about the warning or error', 'Warning or Error',
                          'COUNTA of Information about the warning or error']

    return warningsdf

#creates an API Version tab
def versions(dataframe):
    APIversionsdf = dataframe.groupby(['API Version', 'URL']).count().sort_values(by='API Version').reset_index()
    APIversionsdf = APIversionsdf.groupby(['API Version']).count().sort_values(by='API Version').reset_index()
    APIversionsdf = APIversionsdf[['API Version', 'Warning or Error']]
    APIversionsdf.columns = ['API Version', 'New Total']

    return APIversionsdf

#creates a pass fail tab
def passfailtab(dataframe):
    Pass_fail_df = dataframe
    Pass_fail_df["Warning Total per Row"] = pd.to_numeric(Pass_fail_df["Warning Total per Row"])
    Pass_fail_df[["Warning Total per Row", "Error Total per Row"]] = Pass_fail_df[["Warning Total per Row", "Error Total per Row"]].apply(pd.to_numeric)
    Pass_fail_df = Pass_fail_df.groupby(['Organisation', 'URL'])[['Error Total per Row', "Warning Total per Row"]].sum()
    Pass_fail_df.reset_index(inplace=True)
    Pass_fail_df['Pass or Fail'] = Pass_fail_df['Error Total per Row'].apply(lambda x: 'Fail' if x >= 1 else 'Pass')

    return Pass_fail_df


#input & output path
input_path = os.environ['OUTPUT_DIR']
output_path = os.environ['OUTPUT_DIR']

#final function that takes takes the input_path and then creates a list of htmls through function create_html and returns an Excel Spreadsheet
def create_spreadsheet(input_path):
    listofdfs = []
    htmlpaths = create_htmlpaths(input_path)
    for p in htmlpaths:
        initial_df = create_dataframe(p)
        listofdfs.append(initial_df)

    df = pd.concat(listofdfs)
    df = df.reset_index(drop=True)

    # input variable for csv
    name_description = os.path.join(output_path, 'descriptions.csv')
    # creates a dataframe from it
    new_df = pd.read_csv(name_description)
    # creates join column based off url
    new_df['join'] = new_df['raw_url']
    df['join'] = df['Raw URL']
    # drops duplicates in join column
    no_dupes_new_df = new_df.drop_duplicates(subset='join')
    # merges no duplicated df with df on join column
    no_dupes_finaldf = pd.merge(df, no_dupes_new_df, on='join', how='left')
    # merges df with duplicates with df on join column
    dupes_finaldf = pd.merge(df, new_df, on='join', how='left')
    # drops redundant columns
    no_dupes_finaldf = no_dupes_finaldf.drop(columns=['Description', 'Title', 'join', 'raw_url'])
    dupes_finaldf = dupes_finaldf.drop(columns=['Description', 'Title', 'join', 'raw_url'])

    # creates 3 extra tabs
    warningsdf = createwarningstab(no_dupes_finaldf)
    APIversionsdf = versions(no_dupes_finaldf)
    pass_fail_df = passfailtab(no_dupes_finaldf)

    # no duplicates excel creation
    list_newdfs = [no_dupes_finaldf, warningsdf, APIversionsdf, pass_fail_df]
    sheetnames_list = ['Master Database', 'Warnings-by-url', 'API-Versions-used', 'Pass-Fail']
    newdict = dict(zip(sheetnames_list, list_newdfs))

    todays_date = date.today()
    filename = 'No duplication Linting-results' + str(todays_date)
    with pd.ExcelWriter('{}{}.xlsx'.format(output_path, filename), engine="xlsxwriter", mode="w") as writer:
        for x, y in zip(sheetnames_list, list_newdfs):
            y.to_excel(writer, sheet_name=x, index=False)

    # duplicated excel creation
    dupes_list_newdfs = [dupes_finaldf, warningsdf, APIversionsdf, pass_fail_df]
    dupes_sheetnames_list = ['Master Database', 'Warnings-by-url', 'API-Versions-used', 'Pass-Fail']
    newdict2 = dict(zip(dupes_sheetnames_list, dupes_list_newdfs))

    todays_date = date.today()
    filename = 'Duplicated Linting-results' + str(todays_date)
    with pd.ExcelWriter('{}{}.xlsx'.format(output_path, filename), engine="xlsxwriter", mode="w") as writer:
        for x, y in zip(dupes_sheetnames_list, dupes_list_newdfs):
            y.to_excel(writer, sheet_name=x, index=False)

    return

if __name__ == '__main__':
    create_spreadsheet(input_path)