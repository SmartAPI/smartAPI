"""
SmartAPI Database Persistence Model Tests
"""
import json
import os

import pytest
from elasticsearch import Elasticsearch

from model import APIDoc
from utils.indices import refresh

client = Elasticsearch()
dirname = os.path.dirname(__file__)

# prepare data to be saved in tests
with open(os.path.join(dirname, 'mygene.es.json'), 'r') as file:
    MYGENE = json.load(file)
    MYGENE.pop("_id")

ES_INDEX_NAME = 'smartapi_docs'


@pytest.fixture(autouse=True, scope='module')
def setup_fixture():
    client.delete(ES_INDEX_NAME, "doc0", ignore=404)
    client.delete(ES_INDEX_NAME, "doc1", ignore=404)
    client.create(ES_INDEX_NAME, "doc1", MYGENE)
    refresh()


def test_exists():
    # info.title : "MyDisease.info API"
    assert not APIDoc.exists('doc0')
    assert APIDoc.exists('doc1')
    assert APIDoc.exists('3.0.0', 'openapi')
    assert APIDoc.exists('mygene', '_meta.slug')
    assert not APIDoc.exists('mygene', 'info.title')
    assert APIDoc.exists('mygene.info', 'info.title')
    assert APIDoc.exists('mygene.info api', 'info.title')
    assert APIDoc.exists('api', 'info.title')
    assert not APIDoc.exists('mygene', 'info.title.raw')
    assert not APIDoc.exists('mygene.info', 'info.title.raw')
    assert not APIDoc.exists('mygene.info api', 'info.title.raw')
    assert not APIDoc.exists('api', 'info.title.raw')
    assert APIDoc.exists('MyGene.info API', 'info.title.raw')
    assert APIDoc.exists('mygene.info', 'info.description')


def test_aggregation():
    assert 'Chunlei Wu' in APIDoc.aggregate('info.contact.name')
    assert 'gene' in APIDoc.aggregate()
    assert 'annotation' in APIDoc.aggregate()
    assert 'query' in APIDoc.aggregate()
    assert 'query' in APIDoc.aggregate('tags.name.raw')
    assert 'query' in APIDoc.aggregate('tags.name')
    assert 'tester' in APIDoc.aggregate('_meta.username')
    assert 'mygene' in APIDoc.aggregate('_meta.slug')


def teardown_module():
    client.delete(ES_INDEX_NAME, "doc1", ignore=404)
