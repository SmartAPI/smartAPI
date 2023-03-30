from copy import deepcopy

from biothings.web.auth.authn import DefaultCookieAuthnProvider
from biothings.web.settings.default import ANNOTATION_KWARGS, COMMON_KWARGS, QUERY_KWARGS

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
# traditionally, raw parameter takes two boolean values, smartapi additionally
# support one more intermediate level to return the underscore metadata fields.
# now raw can take 0 (without metadata), 1 (with metadata), and 2 (ES raw).
# additionally, since we have supported meta=1 before, and in similar apps,
# like discovery app, behaving like raw=1, make 'meta' an alias to 'raw'.
COMMON_KWARGS["raw"]["type"] = int
COMMON_KWARGS["raw"]["default"] = 0
COMMON_KWARGS["raw"]["alias"] = "meta"

QUERY_KWARGS = deepcopy(QUERY_KWARGS)
QUERY_KWARGS["*"]["authors"] = {"type": list}
QUERY_KWARGS["*"]["tags"] = {"type": list}

ANNOTATION_KWARGS = deepcopy(ANNOTATION_KWARGS)
# all biothings annotation common keywords are consolidated into
# the GET endpoint because we only use this method to read data
# other methods will be used to modify the records in SmartAPI
ANNOTATION_KWARGS["GET"].update(ANNOTATION_KWARGS.pop("*"))
ANNOTATION_KWARGS["POST"].clear()
# when the id is not present, the annotation endpoint will act like
# a get_all endpoint to scroll over all results through pagination
ANNOTATION_KWARGS["GET"]["id"]["required"] = False
# because SmartAPI documents can be large, set a small default
# return size for get_all operation and limit the maximum to 10,
# as a context, the default is 1000 in traditional biothings apps.
ANNOTATION_KWARGS["GET"]["size"]["default"] = 5
ANNOTATION_KWARGS["GET"]["size"]["max"] = 10
# the from keyword is used with size for pagination in scrolling operation
# add from_ as an alias to be compatible with the earlier version design
ANNOTATION_KWARGS["GET"]["from"] = deepcopy(QUERY_KWARGS["GET"]["from"])
ANNOTATION_KWARGS["GET"]["from"]["default"] = 0
ANNOTATION_KWARGS["GET"]["from"]["alias"] = ("skip", "from_")

# since there's explicit ordering of fields in OpenAPI and Swagger documents,
# turn off the default alphabetical ordering of keys during doc transofrmation.
ANNOTATION_KWARGS["GET"]["_sorted"]["default"] = False

# *****************************************************************************
# Elasticsearch
# *****************************************************************************
# This application only works with ES at localhost:9200
# Do not try to set a different ES host location.
# Use port forwarding to connect to a remote server.
# In order to support ES_HOST configuration,
# Modify both model.py and utils.indices.py
ES_HOST = "localhost:9200"
SMARTAPI_ES_INDEX = "smartapi_docs"
METAKG_ES_INDEX = "smartapi_metakg_docs"
ES_INDICES = {
    "metadata": SMARTAPI_ES_INDEX,
    "metakg": METAKG_ES_INDEX,
}

# *****************************************************************************
# Tornado URL Patterns
# *****************************************************************************
APP_LIST = [
    (r"/api/query/?", "biothings.web.handlers.QueryHandler", {"biothing_type": "metadata"}),
    (r"/api/validate/?", "handlers.api.ValidateHandler"),
    (r"/api/uptime/?", "handlers.api.UptimeHandler"),
    (r"/api/metadata/?", "handlers.api.SmartAPIHandler", {"biothing_type": "metadata"}),
    (r"/api/metadata/(.+)/?", "handlers.api.SmartAPIHandler", {"biothing_type": "metadata"}),
    (r"/api/fields/?", "biothings.web.handlers.MetadataFieldHandler"),
    (r"/api/build/?", "biothings.web.handlers.MetadataSourceHandler"),
    (r"/api/status/?", "biothings.web.handlers.StatusHandler"),
    (r"/api/suggestion/?", "handlers.api.ValueSuggestionHandler"),
    (r"/api/metakg/?", "handlers.api.MetaKGQueryHandler", {"biothing_type": "metakg"}),
    (r"/api/metakg/fields/?", "biothings.web.handlers.MetadataFieldHandler", {"biothing_type": "metakg"}),
]

# biothings web tester will read this
API_PREFIX = "api"

# *****************************************************************************
# Query Service
# *****************************************************************************
ANNOTATION_DEFAULT_SCOPES = ["_id", "_meta.slug"]
ES_QUERY_PIPELINE = "pipeline.SmartAPIQueryPipeline"
ES_QUERY_BUILDER = "pipeline.SmartAPIQueryBuilder"
ES_RESULT_TRANSFORM = "pipeline.SmartAPIResultTransform"

AUTHN_PROVIDERS = [(DefaultCookieAuthnProvider, {})]

STATUS_CHECK = {
    "index": "smartapi_docs",
    "id": "59dce17363dce279d389100834e43648",
}  # MyGene.info API entry
