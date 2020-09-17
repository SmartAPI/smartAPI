''' SmartAPI Configuration '''
# pylint: disable=wildcard-import, unused-wildcard-import, unused-import

from biothings.web.settings.default import *
from config_key import *
from web.api.api_handlers.handlers import APP_LIST as api_app_list
from web.api.query_builder import SmartAPIQueryBuilder
from web.handlers import APP_LIST as web_app_list

# *****************************************************************************
# Credentials
# *****************************************************************************
# Define in config_key.py:
#   COOKIE_SECRET = '<Any Random String>'
#   GITHUB_CLIENT_ID = '<your Github application Client ID>'
#   GITHUB_CLIENT_SECRET = '<your Github application Client Secret>'

# *****************************************************************************
# Elasticsearch
# *****************************************************************************
ES_INDEX = 'smartapi_oas3'
ES_DOC_TYPE = '_doc'

# *****************************************************************************
# Tornado URL Patterns
# *****************************************************************************


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


APP_LIST = []
APP_LIST += add_apps('', web_app_list)
APP_LIST += add_apps('api', api_app_list)

# *****************************************************************************
# Biothings Query Settings
# *****************************************************************************
# Subclass of biothings.web.api.es.query_builder.ESQueryBuilder
ES_QUERY_BUILDER = SmartAPIQueryBuilder
# Keyword Argument Control
QUERY_GET_ESQB_KWARGS.update({'filters': {'default': None, 'type': str}})
# Header Strings
ACCESS_CONTROL_ALLOW_METHODS = 'GET,POST,PUT,DELETE,OPTIONS'
# Only affect API endpoints
DISABLE_CACHING = True
# Heavy operation. Enable on small db only.
ALLOW_RANDOM_QUERY = True
