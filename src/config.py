''' SmartAPI Configuration '''


from config_key import *

# *****************************************************************************
# Credentials
# *****************************************************************************
# Define in <project_folder>/config_key.py:
#   COOKIE_SECRET = '<Any Random String>'
#   GITHUB_CLIENT_ID = '<your Github application Client ID>'
#   GITHUB_CLIENT_SECRET = '<your Github application Client Secret>'

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
    (r'/api/?', 'web.api.handlers.APIHandler'),
    (r'/api/query/?', 'web.api.handlers.BioThingsESQueryHandler', {"biothing_type": "api_doc"}),
    (r'/api/validate/?', 'web.api.handlers.ValidateHandler'),
    (r'/api/metadata/(.+)/?', 'web.api.handlers.APIMetaDataHandler'),
    (r'/api/suggestion/?', 'web.api.handlers.ValueSuggestionHandler'),
    (r'/api/webhook_payload/?', 'web.api.handlers.GitWebhookHandler'),
]

# biothings web tester will read this
API_VERSION = ''
API_PREFIX = 'api'

# *****************************************************************************
# Biothings SDK Settings
# *****************************************************************************
ACCESS_CONTROL_ALLOW_METHODS = 'HEAD,GET,POST,DELETE,PUT,OPTIONS'
ES_QUERY_BUILDER = "web.api.q_builder.SmartAPIQueryBuilder"
DISABLE_CACHING = True