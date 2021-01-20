'''
    Elasticsearch Document Object Model
    - The ES backend is a collection of these documents
    - API_Doc
    Reference: https://schema.org/docs/datamodel.html
'''
import os
import sys

if sys.version_info.major >= 3 and sys.version_info.minor >= 6:
    from hashlib import blake2b
else:
    from pyblake2 import blake2b  # pylint: disable=import-error

from elasticsearch_dsl import *  # pylint: disable=unused-wildcard-import
from elasticsearch_dsl.connections import connections  # pylint: disable=wrong-import-position

# parse environment variables
ES_HOST = os.getenv('ES_HOST', 'localhost:9200')
ES_INDEX_NAME = 'smartapi_oas3'

# create a default connection
connections.create_connection(hosts=ES_HOST)

class DocumentMeta(InnerDoc):
    '''
    _meta field.
    etag: "47ccb-16b4c2a9eb0"
    github_username: "pilare"
    slug: "ilincs"
    timestamp: "2019-06-12T15:22:24.973780"
    url: "http://www.ilincs.org/ilincs/smartapi.yml"
    '''
    github_username = Keyword(required=True)
    timestamp = Date(default_timezone='UTC')
    url = Text(required=True)
    etag = Text()
    slug = Text()

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
        _meta: {etag: "47ccb-16b4c2a9eb0", github_username: "pilare", slug: "ilincs",…}
    }
    OR SWAGGER v2
    {
        info: {contact: {email: "markw@illuminae.com", name: "Mark D Wilkinson", url: "http://fairmetrics.org",…},…}
        swagger: "2.0"
        _id: "fe67b4a16a05d20626a52c3d5efd61cf"
        _meta: {etag: "I", github_username: "markwilkinson", swagger_v2: true,…}
    }
    '''
    _meta = Object(DocumentMeta, required=True)
    info = Object()
    paths = Nested(
        multi=True,
        properties={
            "path": Text(),
            "pathitem": Nested(multi=True)
        })
    tags = Object(multi=True, properties={"name": Keyword()})
    openapi = Text()

    # swagger fields
    swagger = Text()
    basePath = Text()
    host = Text()

    class Meta:
        '''
        Doc Meta
        '''
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
    def exists(cls, value, field="_id"):
        """
        Get ID or none of existing doc with matching field query
        """
        search = cls.search().query('match', **{field: value})
        # TODO what if multiple?
        if search.count() == 1:
            doc = next(iter(search)).to_dict(include_meta=True)
            doc.update(doc.pop('_source'))
            doc.pop('_index')
            return doc['_id']
        else:
            return None

    @classmethod
    def aggregate(cls, agg_name: str, field: str, size: int):
        search = cls.search()
        if not field.endswith(".raw"):
            field = field + ".raw"
        agg = A('terms', field=field, size=size)
        search.aggs.bucket(agg_name, agg)
        response = search.execute()
        return response

    def save(self, *args, **kwargs):  # pylint: disable=signature-differs
        self.meta.id = blake2b(self._meta.url.encode('utf8'), digest_size=16).hexdigest()
        super().save(*args, **kwargs)


class APIStatus(Document):

    '''
    API url and endpoints status
    {
        "uptime_status": "incompatible",
        "uptime_ts": "2021-01-13T17:41:07.599428",
        "url_status": 500
    }
    '''

    uptime_status = Text()
    uptime_ts = Date()
    url_status = Integer()

    class Meta:
        '''
        Doc Meta
        '''
        dynamic = MetaField(False)

    class Index:
        '''
        Associated ES index
        '''
        name = "smartapi_status"
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0
        }

    @classmethod
    def exists(cls, _id):
        '''
        Doc with api status exists
        '''
        search = cls.search().query('match', _id=_id)
        return bool(search.count())

