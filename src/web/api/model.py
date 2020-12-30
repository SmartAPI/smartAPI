
from elasticsearch_dsl import InnerDoc, Keyword, Object, Date, Text, Document, MetaField, Nested, A, Q
from elasticsearch import Elasticsearch

ES_HOST = 'localhost:9200'
ES_INDEX_NAME = 'smartapi_oas3'

client = Elasticsearch()


class DocumentMeta(InnerDoc):
    '''
    _meta field.
    ETag: "47ccb-16b4c2a9eb0"
    github_username: "pilare"
    slug: "ilincs"
    timestamp: "2019-06-12T15:22:24.973780"
    uptime_status: "good"
    uptime_ts: "2020-08-24T00:04:11.790424"
    url: "http://www.ilincs.org/ilincs/smartapi.yml"
    '''
    github_username = Keyword(required=True)
    timestamp = Date(default_timezone='UTC')
    url = Text(required=True)
    uptime_ts = Date(default_timezone='UTC')
    ETag = Text()
    # Generated after registration
    slug = Keyword()
    uptime_status = Text()

class Contact(InnerDoc):
    '''
    email: "marcin.pilarczyk@uc.edu"
    name: "API Support - Marcin Pilarczyk"
    url: "http://www.ilincs.org/ilincs/support"
    x-id: "LINCS DCIC - University of Cincinnati"
    x-role: "responsible organization"
    '''
    email = Text()
    name = Keyword()
    url = Text()

class DocumentInfo(InnerDoc):
    '''
    contact: {email: "marcin.pilarczyk@uc.edu", name: "API Support - Marcin Pilarczyk",…}
    description: "Documentation of the ilincs.org API. Learn more about [ilincs.org](http://www.ilincs.org/ilincs/about)"
    termsOfService: "http://www.ilincs.org/ilincs/about"
    title: "iLINCS API"
    version: "2.6.7"
    '''
    contact = Object(Contact)
    description = Text(required=True)
    termsOfService = Text()
    title = Text(required=True)
    version = Text()

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
        _score: 1
    }
    OR SWAGGER v2
    {
        info: {contact: {email: "markw@illuminae.com", name: "Mark D Wilkinson", url: "http://fairmetrics.org",…},…}
        swagger: "2.0"
        _id: "fe67b4a16a05d20626a52c3d5efd61cf"
        _meta: {ETag: "I", github_username: "markwilkinson", swagger_v2: true,…}
        _score: 1
    }
    '''
    _meta = Object(DocumentMeta, required=True)
    info = Object(DocumentInfo, required=True)
    paths = Nested(
        multi=True,
        properties={
            "path": Text(),
            "pathitem": Nested(multi=True, properties={
                # not sure here changes with method type
            })
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
