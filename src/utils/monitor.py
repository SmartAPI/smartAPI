"""
    API Uptime Monitor
    
    Author:
        Kevin Xin
        Amiteshk Sharma

    Status:
        Pass,
        Fail,
        Incompatible,
        Unknown

"""

import logging
from enum import Enum
import requests
import json

# pylint:disable=import-error, ungrouped-imports
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  # pylint:disable=no-member

# enums class to represent outcomes for cors check


class Cors(Enum):
    ENABLED = 'CORS-Enabled'
    DISABLED = 'CORS-Disabled'
    UNKNOWN = 'CORS-Unknown'

# provide information on total APIs with CORS support
# takes in the total count of APIs provided


class CorsCounter:

    def __init__(self, total_api_count):
        self._enabled = 0       # number of CORS-enabled APIs
        self._disabled = 0      # number of CORS-disabled APIs
        self._unknown = 0       # number of CORS-unknown APIs
        self.total_apis = total_api_count

    # used to increment the correct count
    def increment_count(self, count):
        try:
            if count == -1:
                self._unknown += 1
            elif count > 0:
                self._enabled += 1
            else:
                self._disabled += 1
        except TypeError:
            logger = logging.getLogger('CorsCounter.CorsStatus')
            logger.error('Please pass in a int. ')

    def __str__(self):
        enabled = f"The total number of CORS-enabled APIs out of ({self.total_apis}): ({self._enabled})\n"
        disabled = f"The total number of CORS-disabled APIs out of ({self.total_apis}): ({self._disabled})\n"
        unknown = f"The total number of CORS-unknown APIs out of ({self.total_apis}): ({self._unknown})\n"

        return enabled + disabled + unknown


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
        self._total_cors = 0        # count the number of CORS responses
        self._uptime_msg = []
        try:
            self.name = api_doc['info']['title']
        except KeyError:
            self.name = "No name specified"
        try:
            self.id = api_doc['_id']  # pylint: disable=invalid-name
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

    def test_endpoint(self, _endpoint, _endpoint_info):
        endpoint_doc = {'name': '/'.join(s.strip('/') for s in (self.api_server, _endpoint)),
                            'components': self.components}
        if 'get' in _endpoint_info:
            endpoint_doc['method'] = 'GET'
            endpoint_doc['params'] = _endpoint_info.get('get').get('parameters')
        elif 'post' in _endpoint_info:
            endpoint_doc['method'] = 'POST'
            endpoint_doc['params'] = _endpoint_info.get('post').get('parameters')
            endpoint_doc['requestbody'] = _endpoint_info['post'].get('requestBody')
        if endpoint_doc.get('params') or endpoint_doc.get('requestbody'):
            endpoint = Endpoint(endpoint_doc)
            try:
                response = endpoint.make_api_call()
            except Exception as exception:  # pylint: disable=broad-except
                logger = logging.getLogger("utils.monitor")
                logger.error(exception)
                # exception error message
                self._uptime_msg.append(_endpoint + ": " + type(exception).__name__)
                return 'fail'
            else:
                if response:
                    status = endpoint.check_response_status(response)
                    cors = endpoint.check_cors_status(response)

                    if len(endpoint.msg):
                        self._uptime_msg.extend(endpoint.msg)
                    if cors == 0:
                        self._cors_status = Cors.ENABLED.value
                        self._total_cors = 1
                    else:
                        self._cors_status = Cors.DISABLED.value

                    if status == 200:
                        return 'pass'
                    else:
                        self._uptime_msg.append(_endpoint + ': Got status (' + status + ')')
                        return 'fail'
                else:
                    # endpoint call failure
                    if len(endpoint.msg):
                        self._uptime_msg.extend(endpoint.msg)
                    return 'unknown'

    def check_api_status(self):
        '''
            loop through each endpoint and extract parameter & example $ HTTP method information
        '''
        self._api_status = 'unknown'
        self._cors_status = Cors.UNKNOWN.value
        results = []

        if not self.api_server:
            return

        for _endpoint, _endpoint_info in self.endpoints_info.items():
            res = None
            try:
                res = self.test_endpoint(_endpoint, _endpoint_info)
            except Exception as exception: # pylint: disable=broad-except
                self._uptime_msg.append(_endpoint + ": " + type(exception).__name__)
                res = 'fail'
            if res:
                results.append(res)

        if not 'fail' in results:
            if 'pass' in results:
                self._uptime_msg = ['Everything looks good!']
                self._api_status = 'pass'
            else:
                # msg will be populated during api call
                self._api_status = 'unknown'
        else:
            # msg will be populated during api call
            self._api_status = 'fail'


    def __str__(self):
        return f"{self.id}: {self._api_status}, {self._cors_status} ({self.name})"

    def get_api_status(self):
        return self._api_status, self._uptime_msg

    def get_cors_status(self):
        return self._cors_status

    def get_total_cors(self):
        if self._cors_status == 'CORS-Unknown':
            return -1

        return self._total_cors


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
        self.msg = []

    def make_api_call(self):
        headers = {
            'User-Agent': 'SmartAPI API status monitor',
            'Content-Type': 'application/json'
        }
        url = self.endpoint_name
        logger = logging.getLogger("utils.uptime.endpoint.make_api_call")
        # handle API endpoint which use GET HTTP method
        if self.method == 'GET':
            params = {}
            example = None
            paramsRequired = None
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
                    
                elif 'required' in _param and _param['required'] is True:
                    paramsRequired = True
            # check required params
            if paramsRequired is True and not bool(params):
                self.msg.append(self.endpoint_name + ': ' + 'MissingRequiredParameters')
                return False

            if bool(params):
                response = requests.get(url,
                                        params=params,
                                        verify=False,
                                        timeout=30,
                                        headers=headers)
                return response
            else:
                response = requests.get(url,
                                        timeout=30,
                                        verify=False,
                                        headers=headers)
                return response
        # handle API endpoint which use POST HTTP method
        elif self.method == "POST":
            params = {}
            example = None
            # get example
            if self.requestbody:
                content = self.requestbody.get('content')
                if content and 'application/json' in content:
                    schema = content.get('application/json').get('schema')
                    example = content.get('application/json').get('example')
                    try:
                        example = json.loads(example)
                    except (json.JSONDecodeError, Exception) as e:
                        logger.debug('Error skipping decoding example %s', e)
                        pass
                    if example:
                        logger.debug(url)
                    elif schema:
                        example = schema.get('example')
                        ref = schema.get('$ref')
                        if example:
                            logger.debug(url)
                        elif ref:
                            logger.debug(url)
                            if ref.startswith('#/components/'):
                                component_path = ref[13:]
                                component_path += '/example'
                                logger.debug('component path: %s', component_path)
                                example = DictQuery(self.components).get(component_path)
                                logger.debug('example %s', example)
                # check required body
                bodyRequired = self.requestbody.get('required')
                if bodyRequired is True and not example:
                    return False

            # get params
            if self.params:
                paramsRequired = None
                for _param in self.params:
                    if 'example' in _param:
                        if _param['in'] == 'path':
                            url = url.replace('{' + _param['name'] + '}', _param['example'])
                        elif _param['in'] == 'query':
                            params[_param['name']] = _param['example']
                    elif 'required' in _param and _param['required'] is True:
                        paramsRequired = True
                # check required params
                if paramsRequired is True and not bool(params):
                    self.msg.append(self.endpoint_name + ': ' + 'MissingRequiredParameters')
                    return False

            # case example and params
            if example and bool(params):
                response = requests.post(url,
                                            params=params,
                                            json=example,
                                            timeout=30,
                                            verify=False,
                                            headers=headers)
                if not response.status_code == 200:
                    self.msg.append(self.endpoint_name + ': ' + response.reason)
                return response
            # case example only
            elif example and not bool(params):
                response = requests.post(url,
                                        json=example,
                                        timeout=30,
                                        verify=False,
                                        headers=headers)
                if not response.status_code == 200:
                    self.msg.append(self.endpoint_name + ': ' + response.reason)
                return response
            # case params only
            elif bool(params):
                self.msg.append(self.endpoint_name + ': ' + 'MissingRequestBody')
                response = requests.post(url,
                                            params=params,
                                            timeout=30,
                                            verify=False,
                                            headers=headers)
                if not response.status_code == 200:
                    self.msg.append(self.endpoint_name + ': ' + 'MissingRequestBody')
                return response
            # case url only
            else:
                self.msg.append(self.endpoint_name + ': ' + 'MissingRequestBody')
                response = requests.post(url,
                                            timeout=30,
                                            verify=False,
                                            headers=headers)
                if not response.status_code == 200:
                    self.msg.append(self.endpoint_name + ': ' + 'MissingRequestBody')
                return response

    def check_response_status(self, response):
        return response.status_code

    def check_cors_status(self, response):
        try:
            access_control = response.headers['Access-Control-Allow-Origin']
            if access_control:
                return 0
        except KeyError:
            return 1
        else:
            return 1
