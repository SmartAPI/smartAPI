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
    'doc': 'smartapi_oas3'
}

# *****************************************************************************
# Tornado URL Patterns
# *****************************************************************************
APP_LIST = [
    (r'/api/?', 'web.api.handlers.handlers.APIHandler'),
    (r'/api/query/?', 'web.api.handlers.handlers.BioThingsESQueryHandler'),
    (r'/api/validate/?', 'web.api.handlers.handlers.ValidateHandler'),
    (r'/api/metadata/(.+)/?', 'web.api.handlers.handlers.APIMetaDataHandler'),
    (r'/api/suggestion/?', 'web.api.handlers.handlers.ValueSuggestionHandler'),
    (r'/api/webhook_payload/?', 'web.api.handlers.handlers.GitWebhookHandler'),
]

# biothings web tester will read this
API_VERSION = ''
API_PREFIX = 'api'

# *****************************************************************************
# Biothings SDK Settings
# *****************************************************************************
ACCESS_CONTROL_ALLOW_METHODS = 'HEAD,GET,POST,DELETE,PUT,OPTIONS'
# ES_QUERY_BUILDER = "discovery.pipeline.DiscoveryQueryBuilder"
DISABLE_CACHING = True