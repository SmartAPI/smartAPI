"""
SmartAPI Database Persistence Model Tests
"""
import json
import os

import pytest
from elasticsearch import Elasticsearch

from model import SmartAPIDoc
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
    assert not SmartAPIDoc.exists('doc0')
    assert SmartAPIDoc.exists('doc1')
    assert SmartAPIDoc.exists('3.0.0', 'openapi')
    assert SmartAPIDoc.exists('mygene', '_meta.slug')
    assert not SmartAPIDoc.exists('mygene', 'info.title')
    assert SmartAPIDoc.exists('mygene.info', 'info.title')
    assert SmartAPIDoc.exists('mygene.info api', 'info.title')
    assert SmartAPIDoc.exists('api', 'info.title')
    assert not SmartAPIDoc.exists('mygene', 'info.title.raw')
    assert not SmartAPIDoc.exists('mygene.info', 'info.title.raw')
    assert not SmartAPIDoc.exists('mygene.info api', 'info.title.raw')
    assert not SmartAPIDoc.exists('api', 'info.title.raw')
    assert SmartAPIDoc.exists('MyGene.info API', 'info.title.raw')
    assert SmartAPIDoc.exists('mygene.info', 'info.description')


def test_aggregation():
    assert 'Chunlei Wu' in SmartAPIDoc.aggregate('info.contact.name')
    assert 'gene' in SmartAPIDoc.aggregate()
    assert 'annotation' in SmartAPIDoc.aggregate()
    assert 'query' in SmartAPIDoc.aggregate()
    assert 'query' in SmartAPIDoc.aggregate('tags.name.raw')
    assert 'query' in SmartAPIDoc.aggregate('tags.name')
    assert 'tester' in SmartAPIDoc.aggregate('_meta.username')
    assert 'mygene' in SmartAPIDoc.aggregate('_meta.slug')


def teardown_module():
    client.delete(ES_INDEX_NAME, "doc1", ignore=404)
