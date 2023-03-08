import logging
from collections.abc import Mapping

from model import MetaKGDoc
from .base import AbstractWebEntity

logger = logging.getLogger(__name__)


class MetaKG(AbstractWebEntity, Mapping):
    LOOKUP_FIELDS = []
    MODEL_CLASS = MetaKGDoc

    @classmethod
    def create_doc(cls, metadata):
        doc = MetaKGDoc(**metadata)
        return doc.to_dict(include_meta=True)
