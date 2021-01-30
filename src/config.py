''' SmartAPI Configuration '''

from biothings.web.settings.default import QUERY_KWARGS

from config_key import *

# *****************************************************************************
# Credentials
# *****************************************************************************
# Define in <project_folder>/config_key.py:
#   COOKIE_SECRET = '<Any Random String>'
#   GITHUB_CLIENT_ID = '<your Github application Client ID>'
#   GITHUB_CLIENT_SECRET = '<your Github application Client Secret>'

# *****************************************************************************
# User Input Control
# *****************************************************************************
QUERY_KWARGS['*']['filters'] = {'type': str, 'group': 'esqb'}
QUERY_KWARGS['*']['authors'] = {'type': list, 'group': 'esqb'}
QUERY_KWARGS['*']['tags'] = {'type': list, 'group': 'esqb'}

# *****************************************************************************
# Elasticsearch
# *****************************************************************************
ES_INDICES = {
    'metadata': 'smartapi_docs'
}

# *****************************************************************************
# Tornado URL Patterns
# *****************************************************************************
APP_LIST = [
    (r'/api/?', 'handlers.api.APIHandler'),
    (r'/api/query/?', 'biothings.web.handlers.QueryHandler', {"biothing_type": "metadata"}),
    (r'/api/validate/?', 'handlers.api.ValidateHandler'),
    (r'/api/metadata/?', 'handlers.api.APIHandler'),
    (r'/api/metadata/(.+)/?', 'handlers.api.APIHandler'),
    (r'/api/suggestion/?', 'handlers.api.ValueSuggestionHandler'),
]

# biothings web tester will read this
API_VERSION = ''
API_PREFIX = 'api'

# *****************************************************************************
# Biothings SDK Settings
# *****************************************************************************
ACCESS_CONTROL_ALLOW_METHODS = 'HEAD,GET,POST,DELETE,PUT,OPTIONS'
ES_QUERY_BUILDER = "pipeline.SmartAPIQueryBuilder"
DISABLE_CACHING = True
