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
# all biothings annotation common keywords are consolidated into
# the GET endpoint because we only use this method to read data
# other methods will be used to modify the records in SmartAPI
ANNOTATION_KWARGS['GET'].update(ANNOTATION_KWARGS.pop('*'))
ANNOTATION_KWARGS['POST'].clear()
# when the id is not present, the annotation endpoint will act like
# a get_all endpoint to scroll over all results through pagination
ANNOTATION_KWARGS['GET']['id']['required'] = False
# because SmartAPI documents can be large, set a small default
# return size for get_all operation and limit the maximum to 10,
# otherwise the default is 1000 in traditional biothings applications.
ANNOTATION_KWARGS['GET']['size']['default'] = 5
ANNOTATION_KWARGS['GET']['size']['max'] = 10
# the from keyword is used with size for pagination in scrolling operation
# add from_ as an alias to be compatible with the earlier version design
ANNOTATION_KWARGS['GET']['from'] = deepcopy(QUERY_KWARGS['GET']['from'])
ANNOTATION_KWARGS['GET']['from']['default'] = 0
ANNOTATION_KWARGS['GET']['from']['alias'] = ('skip', 'from_')
# traditionally, raw parameter takes two boolean values, for compatibility
# reason, we additionally support one more level to return the metadata.
# now raw can take 0 (without metadata), 1 (with metadata), and 2 (ES raw).
# additionally, since some operations are performed in the transform stage,
# it's necessary to cc this option to transform group. moreover, since raw=1
# is used to return metadata, and we have supported meta=1 in similar apps
# like discovery app, make meta an alias to raw for convenience.
ANNOTATION_KWARGS['GET']['raw']['type'] = int
ANNOTATION_KWARGS['GET']['raw']['default'] = 0
ANNOTATION_KWARGS['GET']['raw']['group'] = ('control', 'transform')
ANNOTATION_KWARGS['GET']['raw']['alias'] = 'meta'
# since there's internal field ordering for OpenAPI and Swagger documents, by default
# turn off the alphabetical ordering of keys defaulted in most biothings applictaions.
ANNOTATION_KWARGS['GET']['_sorted']['default'] = False

# *****************************************************************************
# Elasticsearch
# *****************************************************************************
ES_INDICES = {'metadata': 'smartapi_docs'}

# *****************************************************************************
# Tornado URL Patterns
# *****************************************************************************
APP_LIST = [
    (r'/api/?', 'handlers.SmartAPIHandler', {"biothing_type": "metadata"}),  # TO REMOVE
    (r'/api/query/?', 'biothings.web.handlers.QueryHandler', {"biothing_type": "metadata"}),
    (r'/api/validate/?', 'handlers.ValidateHandler'),
    (r'/api/metadata/?', 'handlers.SmartAPIHandler', {"biothing_type": "metadata"}),
    (r'/api/metadata/(.+)/?', 'handlers.SmartAPIHandler', {"biothing_type": "metadata"}),
    (r'/api/suggestion/?', 'handlers.ValueSuggestionHandler'),
]

# biothings web tester will read this
API_VERSION = ''
API_PREFIX = 'api'

# *****************************************************************************
# Biothings SDK Settings
# *****************************************************************************
ACCESS_CONTROL_ALLOW_METHODS = 'HEAD,GET,POST,DELETE,PUT,OPTIONS'
ANNOTATION_DEFAULT_SCOPES = ['_id', '_meta.slug']
ES_QUERY_BUILDER = "pipeline.SmartAPIQueryBuilder"
ES_RESULT_TRANSFORM = "pipeline.SmartAPIResultTransform"
DISABLE_CACHING = True
