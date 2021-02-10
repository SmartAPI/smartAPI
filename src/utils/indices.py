import json
import os

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Index
from model import APIDoc

_dirname = os.path.dirname(__file__)
with open(os.path.join(_dirname, 'mapping.json'), 'r') as file:
    SMARTAPI_MAPPING = json.load(file)


def setup():
    """
    Setup Elasticsearch Index.
    Primary index with dynamic template.
    Secondary index with static mappings.
    """

    if not Index(APIDoc.Index.name).exists():
        APIDoc.init()
        elastic = Elasticsearch()
        elastic.indices.put_mapping(
            index=APIDoc.Index.name,
            body=SMARTAPI_MAPPING
        )


def reset():

    index = Index(APIDoc.Index.name)

    if index.exists():
        index.delete()

    setup()


def refresh():

    index = Index(APIDoc.Index.name)
    index.refresh()
