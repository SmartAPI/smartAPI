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
QUERY_KWARGS['*']['filters'] = {'type': str, 'default': None, 'max': 1000, 'group': 'esqb'}
QUERY_KWARGS['*']['authors'] = {'type': list, 'default': None, 'max': 1000, 'group': 'esqb'}
QUERY_KWARGS['*']['tags'] = {'type': list, 'default': None, 'max': 1000, 'group': 'esqb'}

# *****************************************************************************
# Elasticsearch
# *****************************************************************************
ES_INDICES = {
    'api_doc': 'smartapi_oas3'
}

# *****************************************************************************
# Tornado URL Patterns
# *****************************************************************************
APP_LIST = [
    (r'/api/?', 'web.handlers.api.APIHandler'),
    (r'/api/query/?', 'web.handlers.api.BioThingsESQueryHandler', {"biothing_type": "api_doc"}),
    (r'/api/validate/?', 'web.handlers.api.ValidateHandler'),
    (r'/api/metadata/(.+)/?', 'web.handlers.api.APIMetaDataHandler'),
    (r'/api/suggestion/?', 'web.handlers.api.ValueSuggestionHandler'),
    (r'/api/webhook_payload/?', 'web.handlers.api.GitWebhookHandler'),
]

# biothings web tester will read this
API_VERSION = ''
API_PREFIX = 'api'

# *****************************************************************************
# Biothings SDK Settings
# *****************************************************************************
ACCESS_CONTROL_ALLOW_METHODS = 'HEAD,GET,POST,DELETE,PUT,OPTIONS'
ES_QUERY_BUILDER = "web.api.pipeline.SmartAPIQueryBuilder"
DISABLE_CACHING = True