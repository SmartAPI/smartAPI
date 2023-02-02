import logging
from collections.abc import Mapping

from elasticsearch_dsl import connections
from elasticsearch.helpers import bulk

from model import MetaKGDoc
from utils.metakg.parser import Parser
from .base import AbstractWebEntity, decoder

logger = logging.getLogger(__name__)


class MetaKGEntity(AbstractWebEntity, Mapping):
    LOOKUP_FIELDS = []
    MODEL_CLASS = MetaKGDoc

    @classmethod
    def create_by_smartapi(cls, smartapi_entity, include_reasoner=True):
        extra_data = {
            "id": smartapi_entity._id,
            "url": smartapi_entity.url,
        }
        raw_data = smartapi_entity._doc._raw
        original_data = decoder.to_dict(decoder.decompress(raw_data))
        parser = Parser()

        metadatas = parser.get_non_TRAPI_metadatas(original_data, extra_data)
        if include_reasoner:
            metadatas += parser.get_TRAPI_metadatas(original_data, extra_data)

        bulk(connections.get_connection(), [cls.create_doc(metadata) for metadata in metadatas])

    @classmethod
    def create_doc(cls, metadata):
        doc = MetaKGDoc(**metadata)
        return doc.to_dict(include_meta=True)
