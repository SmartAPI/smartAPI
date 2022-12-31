"""
    Elasticsearch Document Object Model for MetaKG
"""
from elasticsearch_dsl import InnerDoc, Keyword, Text, Object

from .base import BaseDoc


ES_INDEX_NAME = 'metakg_docs'


class SmartAPIInnerDoc(InnerDoc):
    metadata = Keyword(required=True)
    id = Keyword(required=True)
    ui = Keyword()


class APIInnerDoc(InnerDoc):
    name = Text()
    smartapi = Object(SmartAPIInnerDoc)
    x_translator = Object(name="x-translator")


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
            "mapping.total_fields.limit": 2500
        }

    def get_url(self):
        return self.api.smartapi.metadata
