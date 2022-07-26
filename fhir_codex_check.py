
import json
import requests
from urllib.parse import urlparse
from urllib.parse import parse_qs
from json.decoder import JSONDecodeError
from requests.auth import HTTPBasicAuth
import csv
import os

fhir_user = os.getenv('FHIR_USER')
fhir_pw = os.getenv('FHIR_PW')
fhir_base_url = os.getenv('FHIR_URL')


def query_successful(query_url, resp_links):

    self_link = ""
    for link in resp_links:
        if link['relation'] == 'self':
            self_link = link['url']

    parsed_url = urlparse(query_url)
    query_url_params = parse_qs(parsed_url.query)

    parsed_url = urlparse(self_link)
    self_link_params = parse_qs(parsed_url.query)

    for param in query_url_params:
        if param not in self_link_params:
            return False

    return True

def execute_query(query):

    query_url = f'{fhir_base_url}{query}'
    resp = requests.get(query_url, headers={"Prefer": 'handling=strict'}, auth=HTTPBasicAuth(
        fhir_user, fhir_pw))

    resp_object = {}
    resp_object['status'] = "success"

    if resp.status_code != 200:
        resp_object['status'] = "failed"

    try:
        resp_object['json'] = resp.json()

        if 'link' in resp_object['json'].keys() and not query_successful(query_url, resp_object['json']['link']):
            resp_object['status'] = "failed"
    except JSONDecodeError:
        resp_object['status'] = "failed"

    return resp_object


with open("codex-test-queries.json", 'r') as f:
    json_input = json.load(f)
    with open('./results/codex-check-results.csv', 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=';',
                                quotechar='"', quoting=csv.QUOTE_MINIMAL)
        header = ['Category', 'Name', 'Code', 'System', 'Status', 'Number Results', 'FHIR Search']
        csv_writer.writerow(header)
        for query in json_input:
            query_result = execute_query(query['query'])

            if query_result['status'] != "failed":
                row_to_write = [query['category'], query['name'], query['code'], query['system'], 'sucess', query_result['json']['total'],query['query_decoded']]
            else:
                row_to_write = [query['category'], query['name'], query['code'], query['system'], 'failed', '', query['query_decoded']]

            csv_writer.writerow(row_to_write)
