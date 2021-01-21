import json
import logging
import os

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Index
from model import APIDoc, APIStatus

dirname = os.path.dirname(__file__)
with open(os.path.join(dirname, 'mapping.json'), 'r') as file:
    SMARTAPI_MAPPING = json.load(file)

def setup_data():

    try:
        if not Index(APIDoc.Index.name).exists():
            # API doc - supports dynamic templates
            elastic = Elasticsearch()
            elastic.indices.create(index=APIDoc.Index.name, ignore=400, body=SMARTAPI_MAPPING)
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
