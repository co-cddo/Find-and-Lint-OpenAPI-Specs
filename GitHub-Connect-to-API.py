import requests
from pprint import pprint

def get_organisations():
    token = ''
    headers = {'Authorization': f'token {token}'}
    query_url = 'https://api.github.com/search/code'
    with open('organisations.txt') as f:
        for line in f:
            organisation = line.strip()
            params = {
                'q' : f'openapi\":\" org:{organisation}',

            }
            r = requests.get(query_url, headers=headers, params=params)
            #pprint(r.json())
            response = r.json()
            items = response['items']
            for x in items:
                print(x['html_url'])






if __name__ == '__main__':
    get_organisations()


