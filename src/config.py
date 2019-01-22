from biothings.web.settings.default import *
from config_key import API_KEY, COOKIE_SECRET, GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET

from api.handlers import APP_LIST as api_app_list
from web.handlers import APP_LIST as web_app_list

from api.query_builder import SmartAPIQueryBuilder

# elasticsearch index name
ES_INDEX = 'smartapi_oas3'
# elasticsearch document type
ES_DOC_TYPE = 'api'

def add_apps(prefix='', app_list=None):
    '''
    Add prefix to each url handler specified in app_list.
    add_apps('test', [('/', testhandler,
                      ('/test2', test2handler)])
    will return:
                     [('/test/', testhandler,
                      ('/test/test2', test2handler)])
    '''
    if not app_list:
        app_list = []
    if prefix:
        return [('/'+prefix+url, handler) for url, handler in app_list]
    else:
        return app_list


APP_LIST = [
    # (r"/", MainHandler),
]

APP_LIST += add_apps('', web_app_list)
APP_LIST += add_apps('api', api_app_list)

ACCESS_CONTROL_ALLOW_METHODS = 'GET,POST,PUT,DELETE,OPTIONS'

ES_QUERY_BUILDER = SmartAPIQueryBuilder

QUERY_GET_ESQB_KWARGS.update({'filters': {'default': None, 'type': str}})

# only disables API endpoint caching, web components are not affected 
DISABLE_CACHING = True