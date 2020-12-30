import pytest

from web.api.controller import APIDocController, RegistryError, get_api_metadata_by_url
from web.api.model import APIDoc

_my_gene_id = '59dce17363dce279d389100834e43648'

_my_disease_id = '48a39f7fb04ea9c5e850264a38113f12'

_test_slug = 'myslug'

_user = {"login": "marcodarko"}

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
        doc = doc.get(id=_my_gene_id)
        doc.delete(id=_my_gene_id)
    # mydisease
    if APIDoc.exists(_my_disease_id):
        doc = APIDoc()
        doc = doc.get(id=_my_disease_id)
        doc.delete(id=_my_disease_id)
    _my_gene = get_api_metadata_by_url(_my_gene_url)
    _my_disease = get_api_metadata_by_url(_my_disease_url)

def test_add_dryrun():
    """
    Dryrun add doc
    """
    with pytest.raises(RegistryError) as err:
        APIDocController.add(
            _my_gene,
            user_name=_user['login'],
            url=_my_gene_url,
            dryrun=True)
        assert err == 'API is valid but this was only a test'

def test_validate_valid():
    """
    valid metadata
    """
    assert APIDocController.validate(_my_gene)

def test_validate_invalid():
    """
    invalid metadata
    """
    assert not APIDocController.validate({'some_field': 'no_meaning'})

def test_add_doc_1():
    """
    Successful addition
    """
    res = APIDocController.add(
        _my_gene,
        user_name=_user['login'],
        url=_my_gene_url)

    assert res.get('_id') == _my_gene_id

def test_add_already_exists():
    """
    API exists
    """
    with pytest.raises(RegistryError) as err:
        APIDocController.add(
            _my_gene,
            user_name=_user['login'],
            url=_my_gene_url)
        assert err == 'API Exists'

def test_add_doc_2():
    """
    Add test My Disease API to index, return new doc ID
    """
    res = APIDocController.add(
        _my_disease,
        user_name=_user['login'],
        url=_my_disease_url)

    assert res.get('_id') == _my_disease_id

def test_get_all():
    """
    Get ALL docs
    """
    docs = APIDocController.get_all()
    assert len(docs) == 2

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
    assert len(docs) == 1

def test_get_one():
    """
    Get one doc by ID
    """
    _id = _my_gene_id

    doc = APIDocController.get_api(api_name=_id)
    assert doc['info']['title'] == 'MyGene.info API'

def test_get_one_no_meta():
    """
    Get one doc without meta field
    """
    _id = _my_gene_id

    doc = APIDocController.get_api(api_name=_id, with_meta=False)
    assert '_meta' not in doc

def test_get_one_raw():
    """
    Get one doc with raw
    """
    _id = _my_gene_id

    doc = APIDocController.get_api(api_name=_id, return_raw=True)
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
    with pytest.raises(RegistryError):
        APIDocController.validate_slug_name(slug_name='smart-api')

def test_validate_slug_invalid_2():
    """
    invalid characters in slug
    """
    with pytest.raises(RegistryError):
        APIDocController.validate_slug_name(slug_name='myname#')

def test_update_slug():
    """
    Update registered slug name for ID
    """
    api_id = _my_gene_id
    slug = _test_slug
    user = _user

    doc = APIDocController(api_id)
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

    doc = APIDocController(api_id)
    res = doc.update_slug(_id=api_id, user=user, slug_name='')
    assert res.get(f'{api_id}._meta.slug', False) == ''

def test_refresh_api():
    """
    Refresh single api with id
    """
    api_id = _my_gene_id
    user = _user

    doc = APIDocController(api_id)
    res = doc.refresh_api(_id=api_id, user=user, test=True)
    assert res.get('test-updated', '') == f"API with ID {api_id} was refreshed"

def teardown_module():
    """ teardown any state that was previously setup.
    """
    print("teardown")
    # TODO make sure its deleted
