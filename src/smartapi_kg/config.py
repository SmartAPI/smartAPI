FILTER_FIELDS = [
    "input_type",
    "output_type",
    "predicate",
    "api_name",
    "source",
]

SMARTAPI_URL = "https://smart-api.info/api/query?q=tags.name:translator&size=500&fields=paths,servers,tags,components.x-bte*,info,_meta&meta=1"

SINGLE_API_SMARTAPI_QUERY_TEMPLATE = "https://smart-api.info/api/metadata/{smartapi_id}"

TEAM_SMARTAPI_QUERY_TEMPLATE = 'https://smart-api.info/api/query?q=info.x-translator.team:"{team_name}"&size=150&fields=paths,servers,tags,components.x-bte*,info,_meta'

COMPONENT_SMARTAPI_QUERY_TEMPLATE = 'https://smart-api.info/api/query?q=info.x-translator.component:"{component_name}"&size=150&fields=paths,servers,tags,components.x-bte*,info,_meta'

TAG_SMARTAPI_QUERY_TEMPLATE = "https://smart-api.info/api/query?q=tags.name:{tag_name}&size=150&fields=paths,servers,tags,components.x-bte*,info,_meta"
