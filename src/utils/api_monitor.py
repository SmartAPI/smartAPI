'''
    API Uptime Monitor

        - Status: Good, Bad, Incompatible, Unknown

        - Run this file directly to perform status check
'''

import logging
from datetime import datetime
from functools import partial

import requests
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from elasticsearch_dsl.connections import connections
# pylint:disable=import-error, ungrouped-imports
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from tornado.ioloop import IOLoop

connections.create_connection(hosts=['localhost'])
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
        self.id = api_doc['_id']  # pylint: disable=invalid-name
        self.api_status = 'unknown'
        self.name = api_doc['info']['title']
        try:
            self.api_server = api_doc['servers'][0]['url']
        except KeyError:
            self.api_server = None
            self.api_status = 'incompatible'
        new_path_info = {}
        if 'paths' in api_doc:
            for _path in api_doc['paths']:
                new_path_info[_path['path']] = _path['pathitem']
        else:
            self.api_status = 'incompatible'
        self.components = api_doc.get('components')
        self.endpoints_info = new_path_info

    def check_api_status(self):
        '''
            loop through each endpoint and extract parameter & example $ HTTP method information
        '''

        if not self.api_server:
            return

        for _endpoint, _endpoint_info in self.endpoints_info.items():
            endpoint_doc = {'name': '/'.join(s.strip('/') for s in(self.api_server, _endpoint)),
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
                    logger = logging.getLogger("utils.uptime.API")
                    logger.error(exception)
                else:
                    if response:
                        status = endpoint.check_response_status(response)
                        if status == 200:
                            self.api_status = 'good'
                        else:
                            self.api_status = 'bad'

    def __str__(self):
        return f"{self.id}: {self.api_status} ({self.name})"


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
                elif 'required' in _param and _param['required'] == True:
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
                elif 'required' in _param and _param['required'] == True:
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


def update_uptime_status():
    """
    Perform Periodic Update to Uptime Status in ES
    """
    logger = logging.getLogger("utils.uptime.update")
    logger.info("Start uptime check...")

    def check_status(doc):
        api = API(doc)
        api.check_api_status()
        return api.api_status

    search = Search(index='smartapi_oas3') \
        .query("match_all") \
        .exclude("term", **{"_meta._archived": "true"})

    total = search.count()
    result = {}

    logger.info("Found %s documents", total)

    for index, hit in enumerate(search.scan()):

        doc = hit.to_dict()
        doc['_id'] = hit.meta.id

        status = check_status(doc)

        logger.info("[%s/%s] %s", index + 1, total, hit.meta.id)

        doc_params = {
            "id": hit.meta.id,
            "index": 'smartapi_oas3',
            "doc_type": 'api'
        }
        partial_update = {
            "doc": {
                "_meta": {
                    "uptime_status": status,
                    "uptime_ts": datetime.utcnow()
                }
            }
        }
        es_client = Elasticsearch()
        res = es_client.update(body=partial_update, **doc_params)

        logger.debug(res)

        result[status] = result.get(status, 0) + 1

    logger.info("Uptime updated. %s", result)


def main():
    """
    Check Production Server API Status

    - Output result to screen and file
    - Do not make changes to es index

    """
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger("utils.uptime.main")
    logger.info("Start checking API status.")

    # call smartapi API to fetch all API metadata in registry
    api_docs = requests.get('https://smart-api.info/api/query?q=__all__&size=100').json()
    logger.info("Retrieved %s api documents.", api_docs['total'])

    # can rename or specify a specific folder to put the file
    output_file_name = 'smarapi_uptime_robot' + datetime.today().strftime('%Y-%m-%d') + '.txt'
    with open(output_file_name, 'w') as f:  # pylint: disable=invalid-name

        for api_doc in api_docs['hits']:
            api = API(api_doc)
            api.check_api_status()
            logger.info("%s : %s", api.id, api.api_status)
            f.write(api.id + '\t' + api.api_status + '\n')

    logger.info("Done.")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
