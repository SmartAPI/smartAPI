"""
SmartAPI Controller Tests
"""
import os

import json
import pytest

from controller import SmartAPI, RegistryError
from model import APIDoc
from utils.indices import refresh

MYGENE_URL = 'https://raw.githubusercontent.com/NCATS-Tangerine/'\
    'translator-api-registry/master/mygene.info/openapi_full.yml'
MYCHEM_URL = 'https://raw.githubusercontent.com/NCATS-Tangerine/'\
    'translator-api-registry/master/mychem.info/openapi_full.yml'
DATEAPI_URL = 'https://raw.githubusercontent.com/JDRomano2/ncats-apis/master/date/openapi_date.yml'
AUTOMAT_URL = 'https://automat.renci.org/panther/openapi.json'

MYGENE_ID = '59dce17363dce279d389100834e43648'
MYCHEM_ID = '8f08d1446e0bb9c2b323713ce83e2bd3'
AUTOMAT_ID = 'a3cfb0c18f630ce73ccf86b1db5117db'
DATEAPI_ID = '26ce0569ba5b82902148069b4c3e51b4'

TEST_SLUG = 'myslug'

USER = {"github_username": "marcodarko"}

dirname = os.path.dirname(__file__)

# prepare data to be saved in tests
with open(os.path.join(dirname, 'mygene.json'), 'r') as file:
    MYGENE_DATA = json.load(file)

with open(os.path.join(dirname, 'mychem.json'), 'r') as file:
    MYCHEM_DATA = json.load(file)

with open(os.path.join(dirname, 'automat.json'), 'r') as file:
    AUTOMAT_DATA = json.load(file)

with open(os.path.join(dirname, 'dateapi.json'), 'r') as file:
    DATEAPI_DATA = json.load(file)

@pytest.fixture(autouse=True, scope='module')
def setup_fixture():
    """
    Prepare data for 2 tests and save 2 documents initially
    """
    test_ids = [MYGENE_ID, MYCHEM_ID, AUTOMAT_ID, DATEAPI_ID]

    # clean up index
    for _id in test_ids:
        if APIDoc.exists(_id):
            doc = APIDoc.get(_id)
            doc.delete()
    # save initial docs with paths already transformed
    doc1 = APIDoc(meta={'id': AUTOMAT_ID}, **AUTOMAT_DATA)
    doc1.save()

    doc2 = APIDoc(meta={'id': DATEAPI_ID}, **DATEAPI_DATA)
    doc2.save()
    # refresh index
    refresh()

def test_get_all():
    """
    Get ALL docs
    """
    docs = SmartAPI.get_all()
    assert len(docs) == 2
    assert docs[0]["info"]["title"] in ["Automat Panther", "DATE API"]
    assert docs[1]["info"]["title"] in ["Automat Panther", "DATE API"]

def test_version():
    """
    metadata version handler
    """
    assert SmartAPI.from_dict(MYGENE_DATA).version == 'v3'

def test_validation():
    """
    valid openapi v3 metadata
    """
    doc = SmartAPI.from_dict(MYGENE_DATA)
    doc.validate()

def test_validate_invalid_v3():
    """
    invalid openapi v3 metadata
    """
    with pytest.raises(RegistryError):
        doc = SmartAPI.from_dict({'some_field': 'no_meaning', 'openapi': '3.0.0'})
        doc.validate()

def test_add_doc_1():
    """
    Successful addition
    """
    assert not APIDoc.exists(MYGENE_ID)
    doc = SmartAPI.from_dict(MYGENE_DATA)
    doc.url = MYGENE_URL
    doc.username = 'marcodarko'
    res = doc.save()
    refresh()
    assert res == MYGENE_ID
    assert APIDoc.exists(MYGENE_ID)

def test_add_doc_2():
    """
    Add test My Disease API to index, return new doc ID
    """
    assert not APIDoc.exists(MYCHEM_ID)
    doc = SmartAPI.from_dict(MYCHEM_DATA)
    doc.url = MYCHEM_URL
    doc.username = 'marcodarko'
    res = doc.save()
    refresh()
    assert res == MYCHEM_ID
    assert APIDoc.exists(MYCHEM_ID)

def test_get_all_size_1():
    """
    Get ALL with size
    """
    search = APIDoc.search()
    assert search.count() > 1

    docs = SmartAPI.get_all(size=1)
    assert len(docs) == 1

def test_get_all_from():
    """
    Get ALL from starting point
    """
    if not APIDoc.exists(MYGENE_ID):
        doc = SmartAPI.from_dict(MYGENE_DATA)
        doc.url = MYGENE_URL
        doc.username = 'marcodarko'
        doc.save()
        refresh()

    if not APIDoc.exists(MYCHEM_ID):
        doc = SmartAPI.from_dict(MYCHEM_DATA)
        doc.url = MYCHEM_URL
        doc.username = 'marcodarko'
        doc.save()
        refresh()

    search = APIDoc.search()
    assert search.count() == 4

    docs = SmartAPI.get_all(from_=1)
    assert len(docs) == 3

def test_get_one():
    """
    Get one doc by ID
    """
    if not APIDoc.exists(MYGENE_ID):
        doc = SmartAPI.from_dict(MYGENE_DATA)
        doc.url = MYGENE_URL
        doc.username = 'marcodarko'
        doc.save()
        refresh()

    assert APIDoc.exists(MYGENE_ID)
    doc = SmartAPI.get_api_by_id(MYGENE_ID)
    assert doc['info']['title'] == 'MyGene.info API'

def test_get_tags_1():
    """
    Get tag aggregations for field (owners)
    """
    if not APIDoc.exists(MYGENE_ID):
        doc = SmartAPI.from_dict(MYGENE_DATA)
        doc.url = MYGENE_URL
        doc.username = 'marcodarko'
        doc.save()
        refresh()

    assert APIDoc.exists(MYGENE_ID)
    res = SmartAPI.get_tags(field='info.contact.name', size=100)
    tags = res.get('aggregations', {}).get('field_values', {}).get('buckets', [])
    assert len(tags) >= 1
    assert [tag for tag in tags if tag['key'] in ['Chunlei Wu']]

def test_get_tags_2():
    """
    Get tag aggregations for field (tags)
    """
    if not APIDoc.exists(MYGENE_ID):
        doc = SmartAPI.from_dict(MYGENE_DATA)
        doc.url = MYGENE_URL
        doc.username = 'marcodarko'
        doc.save()
        refresh()

    assert APIDoc.exists(MYGENE_ID)
    res = SmartAPI.get_tags(field='tags', size=100)
    tags = res.get('aggregations', {}).get('field_values', {}).get('buckets', [])
    assert len(tags) >= 1
    assert [tag for tag in tags if tag['key'] in ['translator']]

def test_validate_slug():
    """
    Update registered slug name for ID
    """
    SmartAPI.validate_slug_name(TEST_SLUG)

def test_validate_slug_invalid_1():
    """
    slug name not allowed
    """
    with pytest.raises(RegistryError) as err:
        SmartAPI.validate_slug_name('smart-api')
    assert str(err.value) == "Slug name smart-api is reserved, please choose another"

def test_validate_slug_invalid_2():
    """
    invalid characters in slug
    """
    with pytest.raises(RegistryError) as err:
        SmartAPI.validate_slug_name('myname#')
    assert str(err.value) == "Slug name myname# contains invalid characters"

def test_update_slug():
    """
    Update registered slug name for ID
    """
    doc = SmartAPI.get_api_by_id(MYGENE_ID)
    doc.slug = TEST_SLUG
    res = doc.save()
    refresh()
    assert APIDoc.exists(TEST_SLUG, '_meta.slug')
    assert res == MYGENE_ID

def test_get_one_by_slug():
    """
    Get one doc by slug
    """
    refresh()
    if not APIDoc.exists(MYGENE_ID):
        doc = SmartAPI.from_dict(MYGENE_DATA)
        doc.url = MYGENE_URL
        doc.username = 'marcodarko'
        doc.slug = TEST_SLUG
        doc.etag = 'I'
        doc.save()
        refresh()

    assert APIDoc.exists(MYGENE_ID)
    assert APIDoc.exists(TEST_SLUG, '_meta.slug')
    refresh()
    doc = SmartAPI.get_api_by_slug(TEST_SLUG)
    assert doc['_id'] == MYGENE_ID

def test_refresh_api():
    """
    Refresh api
    """
    doc = SmartAPI.get_api_by_id(MYGENE_ID)
    new_etag = doc.refresh()
    assert doc.etag == new_etag

def test_delete_doc():
    """
    Delete doc
    """
    refresh()
    if not APIDoc.exists(MYGENE_ID):
        doc = SmartAPI.from_dict(MYGENE_DATA)
        doc.url = MYGENE_URL
        doc.username = 'marcodarko'
        doc.save()
        refresh()

    doc = SmartAPI.get_api_by_id(MYGENE_ID)
    res = doc.delete()
    assert res == MYGENE_ID
    refresh()
    assert not APIDoc.exists(MYGENE_ID)

def teardown_module():
    """
    teardown any state that was previously setup.
    """
    for _id in [AUTOMAT_ID, DATEAPI_ID, MYGENE_ID, MYCHEM_ID]:
        if APIDoc.exists(_id):
            test_doc = APIDoc.get(_id)
            test_doc.delete()
