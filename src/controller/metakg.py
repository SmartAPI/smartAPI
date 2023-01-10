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
from utils.metakg.index import API
from .base import AbstractWebEntity, decoder

logger = logging.getLogger(__name__)


class MetaKGEntity(AbstractWebEntity, Mapping):
    LOOKUP_FIELDS = []
    MODEL_CLASS = MetaKGDoc

    @classmethod
    def create_by_smartapis(cls, smartapi_entities):
        for smartapi_entity in smartapi_entities:
            extra_data = {
                "id": smartapi_entity._id,
                "url": smartapi_entity.url,
            }
            raw_data = smartapi_entity._doc._raw
            original_data = decoder.to_dict(decoder.decompress(raw_data))
            metadatas = cls.get_metadatas(original_data, extra_data)
            for metadata in metadatas:
                cls.create_doc(metadata)

    @classmethod
    def create_doc(cls, metadata):
        doc = MetaKGDoc(**metadata)
        doc._raw = decoder.compress(json.dumps(metadata).encode())
        doc.save()

    @classmethod
    def get_metadatas(cls, data, extra_data=None):
        extra_data = extra_data or {}
        metadatas = []
        parser = API(data)
        for op in parser.metadata["operations"]:
            smartapi_data = op["association"]["smartapi"]
            url = (smartapi_data.get("meta") or {}).get("url") or extra_data.get("url")
            _id = smartapi_data.get("id") or extra_data.get("id")

            metadatas.append({
                "subject": op["association"]["input_type"],
                "object": op["association"]["output_type"],
                "predicate": op["association"]["predicate"],
                "provided_by": op["association"].get("source"),
                "api": {
                    "name": op["association"]["api_name"],
                    "smartapi": {
                        "metadata": url,
                        "id": _id,
                        "ui": f"https://smart-api.info/ui/{_id}"
                    },
                    "x-translator": op["association"]["x-translator"]
                },
            })
        return metadatas
