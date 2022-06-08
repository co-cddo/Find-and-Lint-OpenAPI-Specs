import os
import time

import requests


def find_openapi_docs():
    user_name = os.environ['GITHUB_USERNAME']
    access_token = os.environ['GITHUB_API_TOKEN']
    headers = {'Accept': 'application/vnd.github.v3+json'}
    query_url = 'https://api.github.com/search/code'

    html_urls = []

    with open('organisations.txt') as f:
        lines = f.readlines()
        for line in lines:
            organisation = line.strip()
            params = {
                'q': f'openapi info paths in:file org:{organisation} extension:yml extension:yaml extension:json'
            }
            r = requests.get(query_url, headers=headers, params=params, auth=(user_name, access_token))
            response = r.json()
            items = response['items']
            for item in items:
                html_url = item['html_url']
                if not is_an_archived_repository(item) and 'test' not in item['html_url']:
                    html_urls.append(html_url)
            # Wait to avoid hitting the GitHub API secondary rate limit
            time.sleep(20)

        return html_urls


def convert_to_raw_content_url(html_url):
    new_url = html_url.replace('github.com', 'raw.githubusercontent.com')
    return new_url.replace('/blob', '')


def convert_github_urls_to_raw_content_urls(urls):
    converted_urls = []
    for url in urls:
        url = convert_to_raw_content_url(url)
        converted_urls.append(url)
    return converted_urls


def lint_the_openapi_docs(openapi_docs):
    output_dir = os.environ['OUTPUT_DIR']
    count = 1
    for f in openapi_docs:
        output_file = output_dir + str(count) + '.html'
        os.system('OPENAPI_FILE=' + f + ' OUTPUT_FILE=' + output_file + ' npm run lint:oas')
        count = count + 1


def is_an_archived_repository(item):
    user_name = os.environ['GITHUB_USERNAME']
    access_token = os.environ['GITHUB_API_TOKEN']
    repository_name = item['repository']['full_name']
    query_url = 'https://api.github.com/repos/' + repository_name
    headers = {'Accept': 'application/vnd.github.v3+json'}
    r = requests.get(query_url, headers=headers, auth=(user_name, access_token))
    response = r.json()
    return response['archived']


if __name__ == '__main__':
    openapi_docs = find_openapi_docs()
    raw_openapi_docs = convert_github_urls_to_raw_content_urls(openapi_docs)
    lint_the_openapi_docs(raw_openapi_docs)
