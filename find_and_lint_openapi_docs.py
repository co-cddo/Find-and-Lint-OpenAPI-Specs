import os
import time

import csv
import json
import requests
import yaml
import logging


def find_openapi_docs():
    user_name = os.environ['USERNAME']
    access_token = os.environ['API_TOKEN']
    headers = {'Accept': 'application/vnd.github.v3+json'}
    query_url = 'https://api.github.com/search/code'

    html_urls = []

    with open('organisations.txt') as f:
        lines = f.readlines()
        api_metadata = []
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
                    row = [item['html_url'], get_api_name(html_url), get_api_description(html_url)]
                    api_metadata.append(row)

            # Wait to avoid hitting the GitHub API secondary rate limit
            time.sleep(20)

        write_api_metadata_to_file(api_metadata)
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
        output_file = output_dir + '/' + str(count) + '.html'
        os.system('OPENAPI_FILE=' + f + ' OUTPUT_FILE=' + output_file + ' npm run lint:oas')
        count = count + 1


def is_an_archived_repository(item):
    user_name = os.environ['USERNAME']
    access_token = os.environ['API_TOKEN']
    repository_name = item['repository']['full_name']
    query_url = 'https://api.github.com/repos/' + repository_name
    headers = {'Accept': 'application/vnd.github.v3+json'}
    r = requests.get(query_url, headers=headers, auth=(user_name, access_token))
    response = r.json()
    return response['archived']


def write_api_metadata_to_file(descriptions):
    output_dir = os.environ['OUTPUT_DIR']
    file_path = os.path.join(output_dir, 'descriptions.csv')
    header = ['url', 'name', 'description']
    with open(file_path, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for row in descriptions:
            writer.writerow(row)


def get_raw_openapi_content(url):
    raw_url = convert_to_raw_content_url(url)
    user_name = os.environ['USERNAME']
    access_token = os.environ['API_TOKEN']
    headers = {'Accept': 'application/vnd.github.v3.raw'}
    r = requests.get(raw_url, headers=headers, auth=(user_name, access_token))
    return r.content


def get_api_info_object(html_url):
    content = get_raw_openapi_content(html_url)
    dct = None
    try:
        if html_url.endswith(('.yml', '.yaml')):
            dct = yaml.safe_load(content)
        elif html_url.endswith('json'):
            dct = json.loads(content)
    except (yaml.YAMLError, json.JSONDecodeError):
        logging.info("Error while parsing OpenAPI file")
        return 'N/A'
    if 'info' in dct:
        return dct['info']


def get_api_name(html_url):
    item = get_api_info_object(html_url)
    if 'title' in item:
        return item['title']
    else:
        return 'N/A'


def get_api_description(html_url):
    item = get_api_info_object(html_url)
    if 'description' in item:
        description = item['description']
        description = description.replace('\n', '. ')
        return description.split('. ')[0]
    else:
        return 'N/A'


if __name__ == '__main__':
    openapi_docs = find_openapi_docs()
    raw_openapi_docs = convert_github_urls_to_raw_content_urls(openapi_docs)
    lint_the_openapi_docs(raw_openapi_docs)
