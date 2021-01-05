import pytest
import json

from web.api.controller import APIDocController, RegistryError, get_api_metadata_by_url, V3Metadata, V2Metadata
from web.api.model import APIDoc
from utils.indices import refresh
from .data import TEST1, TEST2

_my_gene_id = '59dce17363dce279d389100834e43648'

_my_disease_id = '48a39f7fb04ea9c5e850264a38113f12'

_test_slug = 'myslug'

_user = {"github_username": "marcodarko"}

_my_gene = {}

_my_disease = {}

_my_gene_url = 'https://raw.githubusercontent.com/NCATS-Tangerine/translator-api-registry/master/mygene.info/openapi_full.yml'

_my_disease_url = 'https://raw.githubusercontent.com/jmbanda/biohack2017_smartAPI/master/AEOLUSsrsAPI-v1.0.json'

@pytest.fixture(autouse=True, scope='module')
def setup_fixture():
    """
    Get data from test urls
    """
    global _my_disease
    global _my_gene
    # mygene
    if APIDoc.exists(_my_gene_id):
        doc = APIDoc()
        doc = doc.get(_my_gene_id)
        doc.delete()
    # mydisease
    if APIDoc.exists(_my_disease_id):
        doc = APIDoc()
        doc = doc.get(_my_disease_id)
        doc.delete()
    # download tests
    _my_gene = get_api_metadata_by_url(_my_gene_url)
    _my_disease = get_api_metadata_by_url(_my_disease_url)
    # save test docs
    test1 = APIDoc(meta={'id': '26ce0569ba5b82902148069b4c3e51b4'}, **json.loads(TEST1))
    test1.save()

    test2 = APIDoc(meta={'id': 'a3cfb0c18f630ce73ccf86b1db5117db'}, **json.loads(TEST2))
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
    assert isinstance(APIDocController.from_dict(_my_gene), V3Metadata)

def test_validation():
    """
    valid openapi v3 metadata
    """
    doc = APIDocController.from_dict(_my_gene)
    doc.validate()

def test_validate_invalid_v3():
    """
    invalid openapi v3 metadata
    """
    with pytest.raises(KeyError):
        doc = V3Metadata({'some_field': 'no_meaning'})
        doc.validate_oas3()

def test_validate_invalid_v2():
    """
    invalid openapi v2 metadata
    """
    with pytest.raises(KeyError):
        doc = V2Metadata({'some_field': 'no_meaning'})
        doc.validate()

def test_add_doc_1():
    """
    Successful addition
    """
    doc = APIDocController.from_dict(_my_gene)
    res = doc.save(
        _my_gene,
        user_name=_user['github_username'],
        url=_my_gene_url)
    refresh()
    assert res == _my_gene_id
    assert APIDoc.exists(_id=_my_gene_id)

def test_add_already_exists():
    """
    API exists
    """
    with pytest.raises(RegistryError) as err:
        doc = APIDocController.from_dict(_my_gene)
        doc.save(
            _my_gene,
            user_name=_user['github_username'],
            url=_my_gene_url)
        assert err == 'API Exists'

def test_add_doc_2():
    """
    Add test My Disease API to index, return new doc ID
    """
    doc = APIDocController.from_dict(_my_disease)
    res = doc.save(
        _my_disease,
        user_name=_user['github_username'],
        url=_my_disease_url)
    refresh()
    assert res == _my_disease_id
    assert APIDoc.exists(_id=_my_disease_id)

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
    _id = _my_gene_id

    doc = APIDocController.get_api(query=_id)
    assert doc['info']['title'] == 'MyGene.info API'

def test_get_one_no_meta():
    """
    Get one doc without meta field
    """
    _id = _my_gene_id

    doc = APIDocController.get_api(query=_id, with_meta=False)
    assert '_meta' not in doc

def test_get_one_raw():
    """
    Get one doc with raw
    """
    _id = _my_gene_id

    doc = APIDocController.get_api(query=_id, return_raw=True)
    assert '~raw' not in doc

def test_get_tags():
    """
    Get tag aggregations for field
    """
    field = 'info.contact.name'
    size = 100

    res = APIDocController.get_tags(field=field, size=size)
    assert len(res.get('aggregations', {}).get('field_values', {}).get('buckets', [])) >= 1

def test_validate_slug():
    """
    Update registered slug name for ID
    """
    APIDocController.validate_slug_name(slug_name=_test_slug)

def test_validate_slug_invalid_1():
    """
    slug name not allowed
    """
    with pytest.raises(RegistryError) as err:
        APIDocController.validate_slug_name(slug_name='smart-api')
        assert err == "Slug name smart-api is reserved, please choose another"

def test_validate_slug_invalid_2():
    """
    invalid characters in slug
    """
    with pytest.raises(RegistryError) as err:
        APIDocController.validate_slug_name(slug_name='myname#')
        assert err == "Slug name myname# contains invalid characters"

def test_update_slug():
    """
    Update registered slug name for ID
    """
    api_id = _my_gene_id
    slug = _test_slug
    user = _user

    doc = APIDocController.from_dict(_my_gene)
    res = doc.update_slug(_id=api_id, user=user, slug_name=slug)
    assert res.get(f'{api_id}._meta.slug', False) == slug

def test_get_api_from_slug():
    """
    Get ID of doc with slug
    """
    slug = _test_slug

    _id = APIDocController.get_api_id_from_slug(slug=slug)
    assert isinstance(_id, str)

def test_model_slug_taken():
    """
    Slug name already exists
    """
    assert APIDocController.slug_is_available(slug=_test_slug) is True

def test_delete_slug():
    """
    Delete slug for ID
    """
    api_id = _my_gene_id
    user = _user

    doc = APIDocController.from_dict(_my_gene)
    res = doc.update_slug(_id=api_id, user=user, slug_name='')
    assert res.get(f'{api_id}._meta.slug', False) == ''

def test_refresh_api():
    """
    Refresh single api with id
    """
    api_id = _my_gene_id
    user = _user

    doc = APIDocController.from_dict(_my_gene)
    res = doc.refresh_api(_id=api_id, user=user)
    assert res.get('updated', '') == f"API with ID {api_id} was refreshed"

def teardown_module():
    """ teardown any state that was previously setup.
    """
    test1 = APIDoc.get('26ce0569ba5b82902148069b4c3e51b4')
    test1.delete()

    test2 = APIDoc.get('a3cfb0c18f630ce73ccf86b1db5117db')
    test2.delete()
