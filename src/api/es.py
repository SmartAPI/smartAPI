from elasticsearch import Elasticsearch


ES_HOST = 'localhost:9200'
ES_INDEX_NAME = 'smartapi'
ES_DOC_TYPE = 'api'


def get_es(es_host=None):
    es_host = es_host or ES_HOST
    es = Elasticsearch(es_host, timeout=120)
    return es

class ESQuery():
    def __init__(self, index=None, doc_type=None, es_host=None):
        self._es = get_es(es_host)
        self._index = index or ES_INDEX_NAME
        self._doc_type = doc_type or ES_DOC_TYPE

    def get_api(self, api_name, fields=None):
        if api_name == 'all':
            query = {'query': {"match_all": {}}}
        else:
            query = {
                "query":{
                    "match" : {
                        "@id": {
                            "query": api_name
                        }
                    }
                }
            }
        if fields:
            query["fields"] = fields
        res = self._es.search(self._index, self._doc_type, query)
        res = [d.get('fields', d.get('_source', {})) for d in res['hits']['hits']]
        if len(res) == 1:
            res = res[0]
        return res

    def query_api(self, q, fields=None, input=True):
        attr_output = "http://smart-api.info/vocab/services.http://smart-api.info/vocab/outputField.http://smart-api.info/vocab/parameterValueType.@value"
        attr_input = "http://smart-api.info/vocab/services.http://smart-api.info/vocab/inputParameter.http://smart-api.info/vocab/parameterDataType.@value"
        attr = attr_input if input else attr_output
        query = {
            "query":{
                "match" : {
                    attr: {
                        "query": q
                    }
                }
            }
        }
        if fields == 'all':
            pass
        elif fields:
            query['fields'] = fields
        else:
            query['fields'] = ['@id', attr_input, attr_output]
        print(query)
        res = self._es.search(self._index, self._doc_type, query)
        return res

    def value_suggestion(self, field):
        """return a list of existing values for the given field."""
        query = {
           "aggs": {
                "field_values": {
                    "terms": {"field" : field}
                }
            }
        }
        res = self._es.search(self._index, self._doc_type, query, search_type='count')
        res = res["aggregations"]
        return res
