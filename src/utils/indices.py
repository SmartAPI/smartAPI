import logging

from elasticsearch_dsl import Index
from elasticsearch import Elasticsearch
from model import APIDoc, APIStatus

from .mapping import smart_api_mapping

def setup_data():

    try:
        if not Index(APIDoc.Index.name).exists():
            # API doc - supports dynamic templates
            elastic = Elasticsearch()
            elastic.indices.create(index=APIDoc.Index.name, ignore=400, body=smart_api_mapping)
    except Exception as exc:
        logging.warning(exc)

    try:
        if not Index(APIStatus.Index.name).exists():
            # API status
            APIStatus.init()
    except Exception as exc:
        logging.warning(exc)


def reset_data():

    index_1 = Index(APIDoc.Index.name)

    if index_1.exists():
        index_1.delete()

    APIDoc.init()

def refresh():

    index_1 = Index(APIDoc.Index.name)
    index_1.refresh()
