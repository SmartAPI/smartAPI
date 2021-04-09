"""
    API Uptime Monitor

    Status:
        Good,
        Bad,
        Incompatible,
        Unknown

"""

import logging

import requests

# pylint:disable=import-error, ungrouped-imports
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  # pylint:disable=no-member


class DictQuery(dict):
    """
    Extract the value from nested json based on path
    """

    def get(self, path, default=None):
        keys = path.split("/")
        val = None

        for key in keys:
            if val:
                if isinstance(val, list):
                    val = [v.get(key, default)
                           if v else None for v in val]  # pylint:disable=not-an-iterable
                else:
                    val = val.get(key, default)
            else:
                val = dict.get(self, key, default)

            if not val:
                break

        return val


class API:
    '''
        An API corresponding to an es document
    '''

    def __init__(self, api_doc):
        # default status of API is unknown, since some APIs doesn't provide
        # examples as values for parameters
        self._api_status = None
        self._cors_status = None
        try: 
            self.name = api_doc['info']['title']
        except KeyError:
            self.name = "No name specified"
        try: 
            self.id = api_doc['_id'] # pylint: disable=invalid-name
        except:
            self.id = "no ID specified"
        try:
            self.api_server = api_doc['servers'][0]['url']
        except KeyError:
            self.api_server = None
            self.api_status = 'incompatible'
        if 'paths' not in api_doc:
            self.api_status = 'incompatible'
        self.components = api_doc.get('components')
        self.endpoints_info = api_doc.get('paths')

    def check_api_status(self):
        '''
            loop through each endpoint and extract parameter & example $ HTTP method information
        '''
        self._api_status = 'unknown'
        self._cors_status = 'CORS-unknown'

        if not self.api_server:
            return

        for _endpoint, _endpoint_info in self.endpoints_info.items():
            endpoint_doc = {'name': '/'.join(s.strip('/') for s in (self.api_server, _endpoint)),
                            'components': self.components}
            if 'get' in _endpoint_info:
                endpoint_doc['method'] = 'GET'
                endpoint_doc['params'] = _endpoint_info.get('get').get('parameters')
            elif 'post' in _endpoint_info:
                endpoint_doc['method'] = 'POST'
                endpoint_doc['params'] = _endpoint_info.get('post').get('parameters')
                endpoint_doc['requestbody'] = _endpoint_info['post'].get('requestBody')
            if endpoint_doc.get('params'):
                endpoint = Endpoint(endpoint_doc)
                try:
                    response = endpoint.make_api_call()
                except Exception as exception:  # pylint: disable=broad-except
                    logger = logging.getLogger("utils.monitor")
                    logger.error(exception)
                else:
                    if response:
                        status = endpoint.check_response_status(response)
                        self._cors_status = endpoint.check_cors_status(response)
                        print("       - Cors status: " + self._cors_status)

                        if status == 200:
                            self._api_status = 'good'
                        else:
                            self._api_status = 'bad'
                    else:
                        print()
                        # status = endpoint.check_response_status(response)
                        # logger = logging.getLogger("utils.monitor.api_status")
                        # logger.warning(_endpoint + ": " + str(status))

    def __str__(self):
        return f"{self.id}: {self._api_status}, {self._cors_status} ({self.name})"

    def get_api_status():
        return self._api_status
    
    def get_cors_status():
        return self._cors_status


class Endpoint:
    '''
        An API Endpoint
    '''

    def __init__(self, endpoint_doc):
        self.endpoint_name = endpoint_doc['name']
        self.method = endpoint_doc['method']
        self.params = endpoint_doc['params']
        self.requestbody = endpoint_doc.get('requestbody')
        self.components = endpoint_doc.get('components')

    def make_api_call(self):
        headers = {
            'User-Agent': 'SmartAPI API status monitor'
        }
        url = self.endpoint_name
        logger = logging.getLogger("utils.uptime.endpoint.make_api_call")
        # handle API endpoint which use GET HTTP method
        if self.method == 'GET':
            params = {}
            example = None
            for _param in self.params:
                # replace parameter with actual example value to construct
                # an API call
                if 'example' in _param:
                    example = True
                    # parameter in path
                    if _param['in'] == 'path':
                        url = url.replace('{' + _param['name'] + '}', _param['example'])
                    # parameter in query
                    elif _param['in'] == 'query':
                        params = {_param['name']: _param['example']}
                    try:
                        response = requests.get(url,
                                                params=params,
                                                verify=False,
                                                timeout=10,
                                                headers=headers)
                        return response
                    except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError):
                        pass
                elif 'required' in _param and _param['required'] is True:
                    example = True
            if not example:
                try:
                    response = requests.get(url,
                                            timeout=10,
                                            verify=False,
                                            headers=headers)
                    return response
                except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError):
                    pass
        # handle API endpoint which use POST HTTP method
        elif self.method == "POST":
            data = {}
            example = None
            for _param in self.params:
                if 'example' in _param:
                    if _param['in'] == 'path':
                        url = url.replace('{' + _param['name'] + '}', _param['example'])
                    elif _param['in'] == 'query':
                        data = {_param['name']: _param['example']}
                    try:
                        response = requests.post(url,
                                                 data=data,
                                                 timeout=10,
                                                 verify=False,
                                                 headers=headers)
                        return response
                    except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError):
                        pass
                elif 'required' in _param and _param['required'] is True:
                    example = True
            if self.requestbody:
                content = self.requestbody.get('content')
                if content and 'application/json' in content:
                    schema = content.get('application/json').get('schema')
                    if schema:
                        example = schema.get('example')
                        ref = schema.get('$ref')
                        if example:
                            logger.debug(url)
                            try:
                                response = requests.post(url,
                                                         timeout=10,
                                                         json=example,
                                                         verify=False,
                                                         headers=headers)
                                return response
                            except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError):
                                pass
                        elif ref:
                            logger.debug(url)
                            if ref.startswith('#/components/'):
                                component_path = ref[13:]
                                component_path += '/example'
                                logger.debug('component path: %s', component_path)
                                example = DictQuery(self.components).get(component_path)
                                logger.debug('example %s', example)
                                if example:
                                    try:
                                        response = requests.post(url,
                                                                 timeout=10,
                                                                 json=example,
                                                                 verify=False,
                                                                 headers=headers)
                                        logger.debug(response)
                                        return response
                                    except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError):
                                        pass

            if not example:
                try:
                    response = requests.post(url,
                                             timeout=10,
                                             verify=False,
                                             headers=headers)
                    return response
                except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError):
                    pass

    def check_response_status(self, response):
        return response.status_code
    
    def check_cors_status(self, response):
        try:
            access_control = response.headers['Access-Control-Allow-Origin']
            if access_control:
                return 'CORS-enabled'
        except KeyError:
            return 'CORS-disabled'
        else:
            return 'CORS-disabled'


import json
import requests
import yaml
import numpy as np

if __name__ == "__main__":
    # data = requests.get("https://smart-api.info/api/metadata/59dce17363dce279d389100834e43648").json()
    # data['_id'] = "59dce17363dce279d389100834e43648"

    with open('./smartapi_20210216.json', 'r') as testing_api:
        testing_apis = json.load(testing_api)

        for api in range(134, 300):
            print("===== start of api here =====   " + str(api) + ".")
            api_list = yaml.load(testing_apis[api]['raw'], Loader=yaml.FullLoader)
            test = API(api_list)
            is_good = test.check_api_status()
            output = test.__str__()
            
            if is_good != 1:
                print(output) 
            print('\n')
