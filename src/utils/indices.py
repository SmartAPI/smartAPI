import json
import os

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Index
from model import APIDoc


def exists():
    return Index(APIDoc.Index.name).exists()


def setup():
    """
    Setup Elasticsearch Index with dynamic template.
    Run it on an open index to update dynamic mapping.
    """
    _dirname = os.path.dirname(__file__)
    with open(os.path.join(_dirname, 'mapping.json'), 'r') as file:
        mapping = json.load(file)

    if not exists():
        APIDoc.init()

    elastic = Elasticsearch()
    elastic.indices.put_mapping(
        index=APIDoc.Index.name,
        body=mapping
    )


def delete():
    Index(APIDoc.Index.name).delete()


def reset():

    if exists():
        delete()

    setup()


def refresh():

    index = Index(APIDoc.Index.name)
    index.refresh()
