"""
SmartAPI Database Persistence Model Tests
"""
import json
import os

import pytest
from model import SmartAPIDoc
from utils import decoder
from utils.indices import delete, refresh, reset

dirname = os.path.dirname(__file__)

# prepare data to be saved in tests
with open(os.path.join(dirname, "mygene.es.json"), "r") as file:
    MYGENE_ES = json.load(file)
    MYGENE_ID = MYGENE_ES.pop("_id")

with open(os.path.join(dirname, "mygene.es.json"), "rb") as file:
    MYGENE_RAW = file.read()

ES_INDEX_NAME = "smartapi_docs_test"


@pytest.fixture(autouse=True, scope="module")
def setup_fixture():
    reset(SmartAPIDoc, index=ES_INDEX_NAME)
    mygene = SmartAPIDoc(meta={"id": "doc1"}, **MYGENE_ES)
    mygene._raw = decoder.compress(MYGENE_RAW)
    mygene.save(index=ES_INDEX_NAME)
    refresh(index=ES_INDEX_NAME)


def test_exists():
    # info.title : "MyDisease.info API"
    assert not SmartAPIDoc.exists("doc0", index=ES_INDEX_NAME)
    assert SmartAPIDoc.exists("doc1", index=ES_INDEX_NAME)
    assert SmartAPIDoc.exists("3.0.0", "openapi", index=ES_INDEX_NAME)
    assert SmartAPIDoc.exists("mygene", "_meta.slug", index=ES_INDEX_NAME)
    assert not SmartAPIDoc.exists("mygene", "info.title", index=ES_INDEX_NAME)
    assert SmartAPIDoc.exists("mygene.info", "info.title", index=ES_INDEX_NAME)
    assert SmartAPIDoc.exists("mygene.info api", "info.title", index=ES_INDEX_NAME)
    assert SmartAPIDoc.exists("api", "info.title", index=ES_INDEX_NAME)
    assert not SmartAPIDoc.exists("mygene", "info.title.raw", index=ES_INDEX_NAME)
    assert not SmartAPIDoc.exists("mygene.info", "info.title.raw", index=ES_INDEX_NAME)
    assert not SmartAPIDoc.exists("mygene.info api", "info.title.raw", index=ES_INDEX_NAME)
    assert not SmartAPIDoc.exists("api", "info.title.raw", index=ES_INDEX_NAME)
    assert SmartAPIDoc.exists("MyGene.info API", "info.title.raw", index=ES_INDEX_NAME)
    assert SmartAPIDoc.exists("mygene.info", "info.description", index=ES_INDEX_NAME)


def test_aggregation():
    assert "Chunlei Wu" in SmartAPIDoc.aggregate("info.contact.name", index=ES_INDEX_NAME)
    assert "gene" in SmartAPIDoc.aggregate(index=ES_INDEX_NAME)
    assert "annotation" in SmartAPIDoc.aggregate(index=ES_INDEX_NAME)
    assert "query" in SmartAPIDoc.aggregate(index=ES_INDEX_NAME)
    assert "query" in SmartAPIDoc.aggregate("tags.name.raw", index=ES_INDEX_NAME)
    assert "query" in SmartAPIDoc.aggregate("tags.name", index=ES_INDEX_NAME)
    assert "tester" in SmartAPIDoc.aggregate("_meta.username", index=ES_INDEX_NAME)
    assert "mygene" in SmartAPIDoc.aggregate("_meta.slug", index=ES_INDEX_NAME)


def teardown_module():
    delete(index=ES_INDEX_NAME)
