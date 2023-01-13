"""
    Elasticsearch Document Object Model for SmartAPI
"""
from elasticsearch_dsl import InnerDoc, Keyword, Date, Text, Integer, InnerDoc, Keyword, Date, Text, Object, Binary

from .base import BaseDoc


ES_INDEX_NAME = 'smartapi_docs'


class StatMeta(InnerDoc):
    """ The _status field. """

    uptime_status = Keyword()
    uptime_msg = Text(index=False)
    uptime_ts = Date()

    refresh_status = Integer()
    refresh_ts = Date()


class UserMeta(InnerDoc):
    """ The _meta field. """
    url = Keyword(required=True)
    slug = Keyword()  # url shortcut
    username = Keyword(required=True)
    date_created = Date(default_timezone='UTC')
    last_updated = Date(default_timezone='UTC')


class SmartAPIDoc(BaseDoc):
    _status = Object(StatMeta)
    _raw = Binary()
    _meta = Object(UserMeta, required=True)

    info = Object()
    servers = Object()
    paths = Object(
        properties={
            "path": Text(),
            "pathitem": Object()
        }
    )
    tags = Object(multi=True)
    openapi = Text()

    # swagger only fields
    swagger = Text()
    basePath = Text()
    host = Text()

    class Index:
        """
        Index Settings
        """
        name = ES_INDEX_NAME
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0,
            "mapping.ignore_malformed": True,
            "mapping.total_fields.limit": 2500
        }

    def get_url(self):
        return self._meta.url
