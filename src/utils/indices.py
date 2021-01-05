import logging

from elasticsearch_dsl import Index
from elasticsearch import Elasticsearch
from web.api.model import APIDoc

from .mapping import smart_api_mapping


def setup_data():

    try:
        if not Index(APIDoc.Index.name).exists():
            # dsl model doc
            # APIDoc.init()
            # supports dynamic templates
            elastic = Elasticsearch()
            body = {}
            mapping = smart_api_mapping
            body.update(mapping)
            elastic.indices.create(index=APIDoc.Index.name, ignore=400, body=body)
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
