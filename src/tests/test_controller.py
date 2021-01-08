import os

import json
import pytest

from controller import APIDocController, RegistryError
from model import APIDoc
from utils.indices import refresh

MYGENE_URL = 'https://raw.githubusercontent.com/NCATS-Tangerine/translator-api-registry/master/mygene.info/openapi_full.yml'
MYCHEM_URL = 'https://raw.githubusercontent.com/NCATS-Tangerine/translator-api-registry/master/mychem.info/openapi_full.yml'
DATEAPI_URL = 'https://raw.githubusercontent.com/JDRomano2/ncats-apis/master/date/openapi_date.yml'
AUTOMAT_URL = 'https://automat.renci.org/panther/openapi.json'

MYGENE_ID = '59dce17363dce279d389100834e43648'
MYCHEM_ID = '8f08d1446e0bb9c2b323713ce83e2bd3'
AUTOMAT_ID = 'a3cfb0c18f630ce73ccf86b1db5117db'
DATEAPI_ID = '26ce0569ba5b82902148069b4c3e51b4'

AUTOMAT_DATA = {}
DATEAPI_DATA = {}
MYGENE_DATA = {}
MYCHEM_DATA = {}

TEST_SLUG = 'myslug'

USER = {"github_username": "marcodarko"}

@pytest.fixture(autouse=True, scope='module')
def setup_fixture():
    """
    Prepare data for 2 tests and save 2 documents initially
    """
    global MYCHEM_DATA
    global MYGENE_DATA
    global AUTOMAT_DATA
    global DATEAPI_DATA

    test_ids = [MYGENE_ID, MYCHEM_ID, AUTOMAT_ID, DATEAPI_ID]
    dirname = os.path.dirname(__file__)

    # clean up index
    for _id in test_ids:
        if APIDoc.exists(_id):
            doc = APIDoc()
            doc = doc.get(_id)
            doc.delete()

    # prepare data to be saved in tests
    with open(os.path.join(dirname, 'mygene.json'), 'r') as file:
        MYGENE_DATA = json.load(file)

    with open(os.path.join(dirname, 'mygene.json'), 'r') as file:
        MYCHEM_DATA = json.load(file)

    # save initial docs
    with open(os.path.join(dirname, 'automat.json'), 'r') as file:
        AUTOMAT_DATA = json.load(file)
        d1 = APIDoc(meta={'id': AUTOMAT_ID}, **AUTOMAT_DATA)
        d1.save()

    with open(os.path.join(dirname, 'dateapi.json'), 'r') as file:
        DATEAPI_DATA = json.load(file)
        d2 = APIDoc(meta={'id': DATEAPI_ID}, **DATEAPI_DATA)
        d2.save()
    # refresh index
    refresh()

@pytest.mark.first
def test_get_all():
    """
    Get ALL docs
    """
    docs = APIDocController.get_all()
    assert len(docs) == 2

def test_version():
    """
    metadata version handler
    """
    assert APIDocController.from_dict(MYGENE_DATA).version == 'v3'

def test_validation():
    """
    valid openapi v3 metadata
    """
    doc = APIDocController.from_dict(MYGENE_DATA)
    doc.validate()

def test_validate_invalid_v3():
    """
    invalid openapi v3 metadata
    """
    with pytest.raises(RegistryError):
        doc = APIDocController.from_dict({'some_field': 'no_meaning', 'openapi': '3.0.0'})
        doc.validate()

def test_add_doc_1():
    """
    Successful addition
    """
    doc = APIDocController.from_dict(MYGENE_DATA)
    res = doc.save(
        MYGENE_DATA,
        user_name=USER['github_username'],
        url=MYGENE_URL)
    refresh()
    assert res == MYGENE_ID
    assert APIDoc.exists(_id=MYGENE_ID)

def test_add_already_exists():
    """
    API exists
    """
    with pytest.raises(RegistryError) as err:
        doc = APIDocController.from_dict(MYGENE_DATA)
        doc.save(
            MYGENE_DATA,
            user_name=USER['github_username'],
            url=MYGENE_URL)
    assert str(err.value) == 'API Exists'

def test_add_doc_2():
    """
    Add test My Disease API to index, return new doc ID
    """
    doc = APIDocController.from_dict(MYCHEM_DATA)
    res = doc.save(
        MYCHEM_DATA,
        user_name=USER['github_username'],
        url=MYCHEM_URL)
    refresh()
    assert res == MYCHEM_ID
    assert APIDoc.exists(_id=MYCHEM_ID)

def test_get_all_size_1():
    """
    Get ALL with size
    """
    docs = APIDocController.get_all(size=1)
    assert len(docs) == 1

def test_get_all_from():
    """
    Get ALL from starting point
    """
    docs = APIDocController.get_all(from_=1)
    assert len(docs) == 3

def test_get_one():
    """
    Get one doc by ID
    """
    doc = APIDocController.get_api_by_id(_id=MYGENE_ID)
    assert doc['info']['title'] == 'MyGene.info API'

def test_get_tags():
    """
    Get tag aggregations for field
    """
    res = APIDocController.get_tags(field='info.contact.name', size=100)
    assert len(res.get('aggregations', {}).get('field_values', {}).get('buckets', [])) >= 1

def test_validate_slug():
    """
    Update registered slug name for ID
    """
    APIDocController.validate_slug_name(TEST_SLUG)

def test_validate_slug_invalid_1():
    """
    slug name not allowed
    """
    with pytest.raises(RegistryError) as err:
        APIDocController.validate_slug_name('smart-api')
    assert str(err.value) == "Slug name smart-api is reserved, please choose another"

def test_validate_slug_invalid_2():
    """
    invalid characters in slug
    """
    with pytest.raises(RegistryError) as err:
        APIDocController.validate_slug_name('myname#')
    assert str(err.value) == "Slug name myname# contains invalid characters"

def test_update_slug():
    """
    Update registered slug name for ID
    """
    doc = APIDocController.from_dict(MYGENE_DATA)
    res = doc.update_slug(MYGENE_ID, slug_name=TEST_SLUG)
    assert res == TEST_SLUG

def test_get_one_by_slug():
    """
    Get one doc by slug
    """
    doc = APIDocController.get_api_by_slug(TEST_SLUG)
    assert doc['_id'] == MYGENE_ID

def test_get_id_from_slug():
    """
    Get ID of doc with slug
    """
    _id = APIDocController.get_api_id_from_slug(TEST_SLUG)
    assert _id == MYGENE_ID

def test_model_slug_taken():
    """
    Slug name is taken
    """
    assert APIDocController.slug_is_available(TEST_SLUG)

def test_delete_slug():
    """
    Delete slug
    """
    doc = APIDocController.from_dict(MYGENE_DATA)
    res = doc.update_slug(MYGENE_ID)
    assert res == ''

def test_refresh_api():
    """
    Refresh api
    """
    doc = APIDocController.from_dict(MYGENE_DATA)
    res = doc.refresh_api(MYGENE_ID)
    assert res == f"API with ID {MYGENE_ID} was refreshed"

def teardown_module():
    """ teardown any state that was previously setup.
    """
    test1 = APIDoc.get(AUTOMAT_ID)
    test1.delete()

    test2 = APIDoc.get(DATEAPI_ID)
    test2.delete()
