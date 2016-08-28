from elasticsearch import Elasticsearch


ES_HOST = 'localhost:9200'
ES_INDEX_NAME = 'smartapi_swagger'
ES_DOC_TYPE = 'api'


def get_es(es_host=None):
    es_host = es_host or ES_HOST
    es = Elasticsearch(es_host, timeout=120)
    return es


def create_index(index_name=None):
    index_name = index_name or ES_INDEX_NAME
    body = {}
    mapping = {
        "api" : {
            "dynamic_templates" : [
                {
                    "template_1" : {
                        "match" : "*",
                        "match_mapping_type" : "string",
                        "mapping" : {
                            "type" : "string",
                            "index" : "analyzed",
                            "fields" : {
                                "raw" : {"type": "string", "index" : "not_analyzed"}
                            }
                        }
                    }
                }
            ]
        }
    }
    mapping = {"mappings": mapping}
    body.update(mapping)
    es = get_es()
    print(es.indices.create(index=index_name, body=body))


def index_swagger(swagger_doc, es=None, index=None, doc_type=None):
    es = es or get_es()
    index = index or ES_INDEX_NAME
    doc_type = doc_type or ES_DOC_TYPE
    _id = swagger_doc['host']
    return es.index(index=index, doc_type=doc_type, body=swagger_doc, id=_id)


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
                        "_id": {
                            "query": api_name
                        }
                    }
                }
            }
        if fields and fields not in ["all", ["all"]]:
            query["_source"] = fields
        res = self._es.search(self._index, self._doc_type, query)
        res = [d.get('fields', d.get('_source', {})) for d in res['hits']['hits']]
        if len(res) == 1:
            res = res[0]
        return res

    def query_api(self, q, fields=None, return_raw=True):
        #attr_output = "http://smart-api.info/vocab/services.http://smart-api.info/vocab/outputField.http://smart-api.info/vocab/parameterValueType.@value"
        #attr_input = "http://smart-api.info/vocab/services.http://smart-api.info/vocab/inputParameter.http://smart-api.info/vocab/parameterDataType.@value"
        #attr_input = "services.inputParameter.parameterDataType"
        #attr = attr_input if input else attr_output
        #query = {
        #    "query":{
        #        "match" : {
        #            attr: {
        #                "query": q
        #            }
        #        }
        #    }
        #}
        query = {
            "query":{
                "query_string" : {
                    "query": q
                }
            }
        }
        if not fields or fields == 'all':
            pass
        else:
            query['_source'] = fields
        #else:
        #    query['_source'] = ['@id', attr_input, attr_output]
        #print(query)
        res = self._es.search(self._index, self._doc_type, body=query)
        if not return_raw:
            _res = res['hits']
            _res['took'] = res['took']
            if "facets" in res:
                _res['facets'] = res['facets']
            for v in _res['hits']:
                del v['_type']
                del v['_index']
                for attr in ['fields', '_source']:
                    if attr in v:
                        v.update(v[attr])
                        del v[attr]
                        break
            res = _res
        return res

    def _do_aggregations(self, _field, agg_name, size):
        query = {
           "aggs": {
                agg_name: {
                    "terms": {
                        "field" : _field,
                        "size": size
                    }
                }
            }
        }
        res = self._es.search(self._index, self._doc_type, query, size=0)
        res = res["aggregations"]
        return res

    def value_suggestion(self, field, size=100, use_raw=True):
        """return a list of existing values for the given field."""
        _field = field + ".raw" if use_raw else field
        agg_name = 'field_values'
        res = self._do_aggregations(_field, agg_name, size)
        if use_raw and not res[agg_name]['buckets']:
            # if *.raw does not return any buckets, try without it.
            res = self._do_aggregations(field, agg_name, size)

        return res
