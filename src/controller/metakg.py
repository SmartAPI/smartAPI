import logging
from collections.abc import Mapping

from model import MetaKGDoc
from utils.metakg.parser import Parser
from .base import AbstractWebEntity, decoder

logger = logging.getLogger(__name__)


class MetaKGEntity(AbstractWebEntity, Mapping):
    LOOKUP_FIELDS = []
    MODEL_CLASS = MetaKGDoc

    @classmethod
    def create_by_smartapis(cls, smartapi_entities, include_reasoner=False):
        for smartapi_entity in smartapi_entities:
            extra_data = {
                "id": smartapi_entity._id,
                "url": smartapi_entity.url,
            }
            raw_data = smartapi_entity._doc._raw
            original_data = decoder.to_dict(decoder.decompress(raw_data))
            parser = Parser()
            metadatas = parser.get_non_TRAPI_metadatas(original_data, extra_data)
            if include_reasoner:
                metadatas += parser.get_TRAPI_metadatas(original_data)
            for metadata in metadatas:
                cls.create_doc(metadata)

    @classmethod
    def create_doc(cls, metadata):
        doc = MetaKGDoc(**metadata)
        doc.save()
