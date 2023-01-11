"""
    MetaKG CRUD Validation and Refresh Operations

    Validation only:

        meta_kg = MetaKG(MetaKG.VALIDATION_ONLY)
        meta_kg.raw = rawbytes
        meta_kg.validate()

    Add a document:

        meta_kg = MetaKG(url)
        meta_kg.raw = rawbytes

        meta_kg.username = username

        meta_kg.validate() # should be called before saving
        meta_kg.save()

        meta_kg.check() # populate uptime status
        meta_kg.refresh() # refresh and populate refresh status, auto validate
        meta_kg.save()

    Modify a document metadata:

        meta_kg = MetaKG.get(_id)
        meta_kg.slug = newslug
        meta_kg.save()

    Delete a document:

        meta_kg = MetaKG.get(_id)
        meta_kg.delete()

"""
import logging
import json
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
        doc._raw = decoder.compress(json.dumps(metadata).encode())
        doc.save()
