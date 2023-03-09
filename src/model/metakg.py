"""
    Elasticsearch Document Object Model for MetaKG
"""
from elasticsearch_dsl import InnerDoc, Keyword, Object, Text

from .base import BaseDoc

ES_INDEX_NAME = "smartapi_metakg_docs"


class SmartAPIInnerDoc(InnerDoc):
    id = Keyword(required=True)


class APIInnerDoc(InnerDoc):
    name = Text()
    smartapi = Object(SmartAPIInnerDoc)


class MetaKGDoc(BaseDoc):
    subject = Text()
    object = Text()
    predicate = Text()
    provided_by = Text()
    api = Object(APIInnerDoc)

    class Index:
        """
        Index Settings
        """

        name = ES_INDEX_NAME
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0,
            "mapping.ignore_malformed": True,
            "mapping.total_fields.limit": 2500,
        }

    def get_url(self):
        return self.api.smartapi.metadata
