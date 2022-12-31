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
from collections.abc import Mapping

from model import MetaKGDoc
from .base import AbstractWebEntity

logger = logging.getLogger(__name__)


class MetaKGEntity(AbstractWebEntity, Mapping):
    LOOKUP_FIELDS = []
    MODEL_CLASS = MetaKGDoc
