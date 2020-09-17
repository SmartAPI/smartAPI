import logging

from elasticsearch_dsl import Index
from ..model.api_doc import API_Doc


def setup_data():

    try:
        if not Index(API_Doc.Index.name).exists():
            # create the mappings in elasticsearch
            API_Doc.init()
    except Exception as exc:
        logging.warning(exc)


def reset_data():

    index_1 = Index(API_Doc.Index.name)

    if index_1.exists():
        index_1.delete()

    API_Doc.init()
    