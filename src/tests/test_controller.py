import os

import pytest
import json

from web.api.controller import APIDocController, RegistryError, Downloader, ValidationError
from web.api.model import APIDoc
from utils.indices import refresh

MYGENE_ID = '59dce17363dce279d389100834e43648'

MYDISEASE_ID = '48a39f7fb04ea9c5e850264a38113f12'

TEST1_ID = '26ce0569ba5b82902148069b4c3e51b4'

TEST2_ID = 'a3cfb0c18f630ce73ccf86b1db5117db'

MYGENE = {}

MYDISEASE = {}

TEST1 = {}

TEST2 = {}

MYGENE_URL = 'https://raw.githubusercontent.com/NCATS-Tangerine/translator-api-registry/master/mygene.info/openapi_full.yml'

MYDISEASE_URL = 'https://raw.githubusercontent.com/jmbanda/biohack2017_smartAPI/master/AEOLUSsrsAPI-v1.0.json'

TEST1_URL = 'https://raw.githubusercontent.com/JDRomano2/ncats-apis/master/date/openapi_date.yml'

TEST2_URL = 'https://automat.renci.org/panther/openapi.json'

TEST_SLUG = 'myslug'

USER = {"github_username": "marcodarko"}

@pytest.fixture(autouse=True, scope='module')
def setup_fixture():
    """
    Get data from test urls
    """
    global MYDISEASE
    global MYGENE
    global TEST1
    global TEST2

    test_ids = [MYGENE_ID, MYDISEASE_ID, TEST1_ID, TEST2_ID]
    # clean up index
    for _id in test_ids:
        if APIDoc.exists(_id):
            doc = APIDoc()
            doc = doc.get(_id)
            doc.delete()
    # prepare data to be saved in tests
    MYGENE = Downloader.get_api_metadata_by_url(MYGENE_URL)
    MYDISEASE = Downloader.get_api_metadata_by_url(MYDISEASE_URL)

    # save initial docs
    TEST1 = Downloader.get_api_metadata_by_url(TEST1_URL)
    test1 = APIDoc(meta={'id': TEST1_ID}, **TEST1)
    test1.save()

    TEST2 = Downloader.get_api_metadata_by_url(TEST2_URL)
    test2 = APIDoc(meta={'id': TEST2_ID}, **TEST2)
    test2.save()

    refresh()

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
    assert APIDocController.from_dict(MYGENE).version == 'v3'

def test_validation():
    """
    valid openapi v3 metadata
    """
    doc = APIDocController.from_dict(MYGENE)
    doc.validate()

def test_validate_invalid_v3():
    """
    invalid openapi v3 metadata
    """
    with pytest.raises(ValidationError):
        doc = APIDocController.from_dict({'some_field': 'no_meaning', 'openapi': '3.0.0'})
        doc.validate()

def test_add_doc_1():
    """
    Successful addition
    """
    doc = APIDocController.from_dict(MYGENE)
    res = doc.save(
        MYGENE,
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
        doc = APIDocController.from_dict(MYGENE)
        doc.save(
            MYGENE,
            user_name=USER['github_username'],
            url=MYGENE_URL)
    assert err == 'API Exists'

def test_add_doc_2():
    """
    Add test My Disease API to index, return new doc ID
    """
    doc = APIDocController.from_dict(MYDISEASE)
    res = doc.save(
        MYDISEASE,
        user_name=USER['github_username'],
        url=MYDISEASE_URL)
    refresh()
    assert res == MYDISEASE_ID
    assert APIDoc.exists(_id=MYDISEASE_ID)

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
    assert err == "Slug name smart-api is reserved, please choose another"

def test_validate_slug_invalid_2():
    """
    invalid characters in slug
    """
    with pytest.raises(RegistryError) as err:
        APIDocController.validate_slug_name('myname#')
    assert err == "Slug name myname# contains invalid characters"

def test_update_slug():
    """
    Update registered slug name for ID
    """
    doc = APIDocController.from_dict(MYGENE)
    res = doc.update_slug(_id=MYGENE_ID, user=USER, slug_name=TEST_SLUG)
    assert res.get(f'{MYGENE_ID}._meta.slug', False) == slug

def test_get_id_from_slug():
    """
    Get ID of doc with slug
    """
    _id = APIDocController.get_api_id_from_slug(TEST_SLUG)
    assert isinstance(_id, str)

def test_model_slug_taken():
    """
    Slug name already exists
    """
    assert not APIDocController.slug_is_available(TEST_SLUG)

def test_delete_slug():
    """
    Delete slug for ID
    """
    doc = APIDocController.from_dict(MYGENE)
    res = doc.update_slug(_id=MYGENE_ID, user=USER, slug_name='')
    assert res.get(f'{MYGENE_ID}._meta.slug', False) == ''

def test_refresh_api():
    """
    Refresh single api with id
    """
    doc = APIDocController.from_dict(MYGENE)
    res = doc.refresh_api(_id=MYGENE_ID, user=USER)
    assert res.get('updated', '') == f"API with ID {MYGENE_ID} was refreshed"

def teardown_module():
    """ teardown any state that was previously setup.
    """
    test1 = APIDoc.get(TEST1_ID)
    test1.delete()

    test2 = APIDoc.get(TEST2_ID)
    test2.delete()
