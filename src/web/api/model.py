
from elasticsearch_dsl import InnerDoc, Keyword, Object, Date, Text, Document, MetaField, Nested, A, Q
from elasticsearch import Elasticsearch

ES_HOST = 'localhost:9200'
ES_INDEX_NAME = 'smartapi_oas3'

client = Elasticsearch()


class APIDoc(Document):

    '''
    get, delete and update methods are included by default by elasticsearch_dsl


    OPENAI v3:
    {
        info: {contact: {email: "marcin.pilarczyk@uc.edu", name: "API Support - Marcin Pilarczyk",…},…}
        openapi: "3.0.0"
        paths: [{
            path: "/GeneInfos/{id}/exists"
            pathitem: {get: {summary: "Check whether a model instance exists in the data source."}}
        }],
        tags: [{name: "GeneInfo"}, {name: "SignatureMeta"}, {name: "MeasurementMetaData"}, {name: "SearchTerm"},…]
        _id: "bee3622cff00265a07cf3fd9828be2bf"
        _meta: {ETag: "47ccb-16b4c2a9eb0", github_username: "pilare", slug: "ilincs",…}
    }
    OR SWAGGER v2
    {
        info: {contact: {email: "markw@illuminae.com", name: "Mark D Wilkinson", url: "http://fairmetrics.org",…},…}
        swagger: "2.0"
        _id: "fe67b4a16a05d20626a52c3d5efd61cf"
        _meta: {ETag: "I", github_username: "markwilkinson", swagger_v2: true,…}
    }
    '''
    _meta = Object(multi=True)
    info = Object(multi=True)
    paths = Nested(
        multi=True,
        properties={
            "path": Text(),
            "pathitem": Nested(multi=True)
        })
    tags = Object(multi=True, properties={"name": Keyword()})
    # only one can exist
    swagger = Text()
    openapi = Text()
    basePath = Text()
    host = Text()

    class Meta:
        dynamic = MetaField(True)

    class Index:
        '''
        Associated ES index
        '''
        name = ES_INDEX_NAME
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0
        }

    @classmethod
    def exists(cls, _id):
        search = cls.search().query('match', _id=_id)
        return bool(search.source(False).execute().hits)

    @classmethod
    def get_api_from_slug(cls, slug):
        s = cls.search()
        s.query = Q('bool', should=[Q('match', _meta__slug=slug, size=1)])
        res = s.execute().to_dict()
        return res

    @classmethod
    def aggregate(cls, agg_name: str, field: str, size: int):
        s = cls.search()
        if ".raw" not in field:
            field = field + ".raw"
        a = A('terms', field=field, size=size)
        s.aggs.bucket(agg_name, a)
        response = s.execute()
        return response
   
    @classmethod
    def slug_exists(cls, slug):
        s = cls.search()
        s.query = Q('bool', should=[Q('match', _meta__slug=slug)])
        res = s.execute().to_dict()
        return bool(res['hits']['total']['value'])
