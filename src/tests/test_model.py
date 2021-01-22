"""
SmartAPI DSL Document tests
"""
import json
import os

import pytest
from elasticsearch import Elasticsearch
from model import APIDoc
from utils.indices import refresh

ES_INDEX_NAME = 'smartapi_oas3'
MYDISEASE_ID = 'f307760715d91908d0ae6de7f0810b22'

client = Elasticsearch()

dirname = os.path.dirname(__file__)

# prepare data to be saved in tests
with open(os.path.join(dirname, 'mydisease.json'), 'r') as file:
    MYDISEASE_DATA = json.load(file)

@pytest.fixture(autouse=True, scope='module')
def setup_fixture():
    """
    Get data from test urls
    """
    if client.exists(ES_INDEX_NAME, MYDISEASE_ID):
        client.delete(ES_INDEX_NAME, MYDISEASE_ID)

def test_001_save():
    """
    Save doc
    """
    assert not client.exists(ES_INDEX_NAME, MYDISEASE_ID)
    new_doc = APIDoc(**MYDISEASE_DATA)
    new_doc.save()
    refresh()
    assert APIDoc.exists(MYDISEASE_ID)

def test_002_doc_exists():
    """
    Existing ID exists
    """
    assert APIDoc.exists(MYDISEASE_ID)

def test_003_doc_does_not_exist():
    """
    Fake ID does not exists
    """
    assert not APIDoc.exists('id123779328749279')

def test_004_slug_available():
    """
    Slug name is available
    """
    assert not APIDoc.exists('new_slug', field="._meta.slug")

def test_005_tag_aggregation():
    """
    Confirm aggregations exists for field, eg. tags
    """
    res = APIDoc.aggregate(field='info.contact.name', size=100, agg_name='field_values').to_dict()
    assert len(res.get('aggregations', {}).get('field_values', {}).get('buckets', [])) >= 1

def test_006_delete_doc():
    """
    delete doc
    """
    refresh()
    if not client.exists(ES_INDEX_NAME, MYDISEASE_ID):
        new_doc = APIDoc(**MYDISEASE_DATA)
        new_doc.save()
        refresh()

    doc = APIDoc.get(MYDISEASE_ID)
    doc.delete()
    refresh()
    assert not client.exists(ES_INDEX_NAME, MYDISEASE_ID)

def teardown_module():
    """ teardown any state that was previously setup.
    """
    if client.exists(ES_INDEX_NAME, MYDISEASE_ID):
        client.delete(ES_INDEX_NAME, MYDISEASE_ID)
