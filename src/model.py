'''
    Elasticsearch Document Object Model
    - The ES backend is a collection of these documents
    - API_Doc
    Reference: https://schema.org/docs/datamodel.html
'''
import base64
import gzip
import json
import os
import sys

if sys.version_info.major >= 3 and sys.version_info.minor >= 6:
    from hashlib import blake2b
else:
    from pyblake2 import blake2b  # pylint: disable=import-error

from elasticsearch_dsl import *  # pylint: disable=unused-import
from elasticsearch_dsl.connections import connections

# parse environment variables
ES_HOST = os.getenv('ES_HOST', 'localhost:9200')
ES_INDEX_NAME = 'smartapi_oas3'

# create a default connection
connections.create_connection(hosts=ES_HOST)

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
    openapi = Text()

    # swagger fields
    swagger = Text()
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
    def exists(cls, value, field="_id"):
        search = cls.search().query('match', **{field: value})
        return bool(search.count())

    @classmethod
    def aggregate(cls, agg_name: str, field: str, size: int):
        s = cls.search()
        if not field.endswith(".raw"):
            field = field + ".raw"
        a = A('terms', field=field, size=size)
        s.aggs.bucket(agg_name, a)
        response = s.execute()
        return response

    def save(self, *args, **kwargs):
        _raw = json.dumps(self.to_dict()).encode('utf-8')
        _raw = base64.urlsafe_b64encode(gzip.compress(_raw)).decode('utf-8')
        self["~raw"] = _raw
        self.meta.id = blake2b(self._meta.url.encode('utf8'), digest_size=16).hexdigest()
        super().save(*args, **kwargs)


class APIStatus(Document):

    '''
    API url and endpoints status
    '''

    uptime_status = Text()
    uptime_ts = Date()
    url_status = Integer()

    class Meta:
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
        search = cls.search().query('match', _id=_id)
        return bool(search.count())

