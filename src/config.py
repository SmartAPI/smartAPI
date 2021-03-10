''' SmartAPI Configuration '''

from copy import deepcopy

from biothings.web.settings.default import QUERY_KWARGS, ANNOTATION_KWARGS

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
QUERY_KWARGS = deepcopy(QUERY_KWARGS)
QUERY_KWARGS['*']['authors'] = {'type': list, 'group': 'esqb'}
QUERY_KWARGS['*']['tags'] = {'type': list, 'group': 'esqb'}

ANNOTATION_KWARGS = deepcopy(ANNOTATION_KWARGS)
ANNOTATION_KWARGS['GET'].update(ANNOTATION_KWARGS.pop('*'))
ANNOTATION_KWARGS['GET']['id']['required'] = False
ANNOTATION_KWARGS['GET']['size']['default'] = 5
ANNOTATION_KWARGS['GET']['size']['max'] = 10
ANNOTATION_KWARGS['GET']['raw']['type'] = int
ANNOTATION_KWARGS['GET']['raw']['default'] = 0
ANNOTATION_KWARGS['GET']['raw']['group'] = ('control', 'transform')
ANNOTATION_KWARGS['GET']['raw']['alias'] = 'meta'
ANNOTATION_KWARGS['GET']['from'] = deepcopy(QUERY_KWARGS['GET']['from'])
ANNOTATION_KWARGS['GET']['from']['default'] = 0
ANNOTATION_KWARGS['GET']['from']['alias'] = ('skip', 'from_')
ANNOTATION_KWARGS['GET']['_source']['group'] = 'transform'
ANNOTATION_KWARGS['GET']['_sorted']['default'] = False
ANNOTATION_KWARGS['POST'].clear()

# *****************************************************************************
# Elasticsearch
# *****************************************************************************
ES_INDICES = {'metadata': 'smartapi_docs'}

# *****************************************************************************
# Tornado URL Patterns
# *****************************************************************************
APP_LIST = [
    (r'/api/?', 'handlers.api.SmartAPIHandler', {"biothing_type": "metadata"}),
    (r'/api/query/?', 'biothings.web.handlers.QueryHandler', {"biothing_type": "metadata"}),
    (r'/api/validate/?', 'handlers.api.ValidateHandler'),
    (r'/api/metadata/?', 'handlers.api.SmartAPIHandler', {"biothing_type": "metadata"}),
    (r'/api/metadata/(.+)/?', 'handlers.api.SmartAPIHandler', {"biothing_type": "metadata"}),
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
ES_RESULT_TRANSFORM = "pipeline.SmartAPIResultTransform"
DISABLE_CACHING = True
