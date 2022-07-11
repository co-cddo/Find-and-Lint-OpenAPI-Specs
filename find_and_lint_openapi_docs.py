import os
import time

import csv
import json
import requests
import yaml
import logging


def find_apis():
    user_name = os.environ['USERNAME']
    access_token = os.environ['API_TOKEN']
    headers = {'Accept': 'application/vnd.github.v3+json'}
    query_url = 'https://api.github.com/search/code'
    api_details = []

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
                test_repos = ["test", "Test"]
                if not is_an_archived_repository(item) and not any(
                        x in html_url for x in test_repos) and get_api_info_object(html_url):
                    info_object = get_api_info_object(html_url)
                    api_details.append([convert_to_raw_content_url(html_url), html_url, get_api_name(info_object), get_api_description(info_object), get_api_version(info_object), get_organisation_name(organisation), get_last_commit_date(item)])

            # Wait to avoid hitting the GitHub API secondary rate limit
            time.sleep(20)

        return api_details


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
        output_file = os.path.join(output_dir, str(count) + '.html')
        os.system('OPENAPI_FILE=' + f[0] + ' OUTPUT_FILE=' + output_file + ' npm run lint:oas')
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


def write_api_metadata_to_file(apis):
    output_dir = os.environ['OUTPUT_DIR']
    file_path = os.path.join(output_dir, 'descriptions.csv')
    header = ['raw_url', 'url', 'name', 'description', 'Version of API Doc', 'org name', 'Repo last updated']
    with open(file_path, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for api in apis:
            writer.writerow(api)


def get_raw_openapi_content(url):
    raw_url = convert_to_raw_content_url(url)
    user_name = os.environ['USERNAME']
    access_token = os.environ['API_TOKEN']
    headers = {'Accept': 'application/vnd.github.v3.raw'}
    r = requests.get(raw_url, headers=headers, auth=(user_name, access_token))
    return r.content


def get_api_info_object(html_url):
    content = get_raw_openapi_content(html_url)
    deserialized_content = {}
    try:
        if html_url.endswith(('.yml', '.yaml')):
            deserialized_content = yaml.safe_load(content)
        elif html_url.endswith('json'):
            deserialized_content = json.loads(content)
    except (yaml.YAMLError, json.JSONDecodeError):
        logging.info("Error while parsing OpenAPI file")
        return 'N/A'
    if 'info' in deserialized_content:
        return deserialized_content['info']
    else:
        return {}


def get_api_name(info_object):
    if 'title' in info_object:
        return info_object['title']
    else:
        return 'N/A'


def get_api_description(info_object):
    if 'description' in info_object:
        description = info_object['description']
        description = description.replace('\n', '. ')
        return description.split('. ')[0]
    else:
        return 'N/A'


def get_api_version(info_object):
    if 'version' in info_object:
        return info_object['version']
    else:
        return 'N/A'


def get_organisation_name(organisation):
    user_name = os.environ['USERNAME']
    access_token = os.environ['API_TOKEN']
    query_url = 'https://api.github.com/orgs/' + organisation
    headers = {'Accept': 'application/vnd.github.v3+json'}
    r = requests.get(query_url, headers=headers, auth=(user_name, access_token))
    response = r.json()
    return response['name']


def get_last_commit_date(item):
    user_name = os.environ['USERNAME']
    access_token = os.environ['API_TOKEN']
    repository_name = item['repository']['full_name']
    query_url = 'https://api.github.com/repos/' + repository_name + '/commits'
    headers = {'Accept': 'application/vnd.github.v3+json'}
    params = {'per_page': 1}
    r = requests.get(query_url, headers=headers, auth=(user_name, access_token), params=params)
    response = r.json()
    return response[0]['commit']['committer']['date']


if __name__ == '__main__':
    apis = find_apis()
    write_api_metadata_to_file(apis)
    lint_the_openapi_docs(apis)
