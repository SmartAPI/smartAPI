from datetime import datetime
import requests
import logging


class API:
    def __init__(self, api_doc):
        self.name = api_doc['info']['title']
        self.api_server = api_doc['servers'][0]['url']
        self.endpoints_info = api_doc['paths']
        # default status of API is unknown, since some APIs doesn't provide
        # examples as values for parameters
        self.api_status = 'unknown'

    def check_api_status(self):
        # loop through each endpoint and extract parameter & example $ HTTP
        # method information
        for _endpoint, _endpoint_info in self.endpoints_info.items():
            endpoint_doc = {'name': self.api_server + _endpoint}
            if 'get' in _endpoint_info:
                endpoint_doc['method'] = 'GET'
                if 'parameters' in _endpoint_info['get']:
                    endpoint_doc['params'] = _endpoint_info['get']['parameters']
            elif 'post' in _endpoint_info:
                endpoint_doc['method'] = 'POST'
                if 'parameters' in _endpoint_info['post']:
                    endpoint_doc['params'] = _endpoint_info['post']['parameters']
            if 'params' in endpoint_doc:
                endpoint = Endpoint(endpoint_doc)
                response = endpoint.make_api_call()
                if response:
                    status = endpoint.check_response_status(response)
                    if status == 200:
                        self.api_status = 'good'
                    else:
                        self.api_status = 'bad'


class Endpoint:
    def __init__(self, endpoint_doc):
        self.endpoint_name = endpoint_doc['name']
        self.method = endpoint_doc['method']
        self.params = endpoint_doc['params']

    def make_api_call(self):
        url = self.endpoint_name
        # handle API endpoint which use GET HTTP method
        if self.method == 'GET':
            params = {}
            for _param in self.params:
                # replace parameter with actual example value to construct
                # an API call
                if 'example' in _param:
                    # parameter in path
                    if _param['in'] == 'path':
                        url = url.replace('{' + _param['name'] + '}', _param['example'])
                    # parameter in query
                    elif _param['in'] == 'query':
                        params = {_param['name']: _param['example']}
                    try:
                        response = requests.get(url, params=params, timeout=5)
                        return response
                    except requests.exceptions.ConnectTimeout:
                        pass
        # handle API endpoint which use POST HTTP method
        elif self.method == "POST":
            data = {}
            for _param in self.params:
                if 'example' in _param:
                    if _param['in'] == 'path':
                        url = url.replace('{' + _param['name'] + '}', _param['example'])
                    elif _param['in'] == 'query':
                        data = {_param['name']: _param['example']}
                    try:
                        response = requests.post(url, data=data, timeout=5)
                        return response
                    except requests.exceptions.ConnectTimeout:
                        pass

    def check_response_status(self, response):
        return response.status_code


if __name__ == '__main__':
    # call smartapi API to fetch all API metadata in registry
    api_docs = requests.get('https://smart-api.info/api/metadata/all?size=100').json()
    output_file_name = 'smarapi_uptime_robot_' + datetime.today().strftime('%Y-%m-%d') + '.txt'
    with open(output_file_name, 'w') as f:
        for api_doc in api_docs:
            try:
                api = API(api_doc)
                logging.info('currently processing API')
                api.check_api_status()
                f.write(api.name + '\t' + api.api_status + '\n')
            except KeyError:
                pass


