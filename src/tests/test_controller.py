"""
SmartAPI Controller Tests
"""
from datetime import datetime, timezone
import json
import os

import elasticsearch
import pytest
from controller import ConflictError, ControllerError, NotFoundError, SmartAPI
from model import APIDoc
from utils import decoder
from utils.downloader import File
from utils.indices import refresh, reset

MYGENE_URL = 'https://raw.githubusercontent.com/NCATS-Tangerine/'\
    'translator-api-registry/master/mygene.info/openapi_minimum.yml'
MYCHEM_URL = 'https://raw.githubusercontent.com/NCATS-Tangerine/'\
    'translator-api-registry/master/mychem.info/openapi_full.yml'

MYGENE_ID = '67932b75e2c51d1e1da2bf8263e59f0a'
MYCHEM_ID = '8f08d1446e0bb9c2b323713ce83e2bd3'


dirname = os.path.dirname(__file__)

# prepare data to be saved in tests
with open(os.path.join(dirname, 'mygene.es.json'), 'r') as file:
    MYGENE_ES = json.load(file)

with open(os.path.join(dirname, 'mychem.es.json'), 'r') as file:
    MYCHEM_ES = json.load(file)

with open(os.path.join(dirname, 'mygene.yml'), 'rb') as file:
    MYGENE_RAW = file.read()

with open(os.path.join(dirname, 'mychem.yml'), 'rb') as file:
    MYCHEM_RAW = file.read()


MYGENE_ID = MYGENE_ES.pop("_id")
MYCHEM_ID = MYCHEM_ES.pop("_id")


@pytest.fixture(autouse=True, scope='module')
def setup_fixture():
    """
    Index 2 documents.
    """
    reset()
    # save initial docs with paths already transformed
    mygene = APIDoc(meta={'id': MYGENE_ID}, **MYGENE_ES)
    mygene._raw = decoder.compress(MYGENE_RAW)
    mygene.save()

    mychem = APIDoc(meta={'id': MYCHEM_ID}, **MYCHEM_ES)
    mychem._raw = decoder.compress(MYCHEM_RAW)
    mychem.save()

    # refresh index
    refresh()


def test_get_all():
    """
    SmartAPI.get_all()
    """
    docs = list(SmartAPI.get_all())
    assert len(docs) == 2
    assert docs[0]["info"]["title"] in ["MyGene.info API", "MyChem.info API"]
    assert docs[1]["info"]["title"] in ["MyGene.info API", "MyChem.info API"]


def test_get_all_size():
    """
    SmartAPI.get_all(size=1)
    """
    search = APIDoc.search()
    assert search.count() == 2

    docs = list(SmartAPI.get_all(size=1))
    assert len(docs) == 1


def test_get_all_from():
    """
    SmartAPI.get_all(from_=1)
    """
    search = APIDoc.search()
    assert search.count() == 2

    docs = list(SmartAPI.get_all(from_=1))
    assert len(docs) == 1


def test_get():
    """
    smartapi = SmartAPI.get(_id)
    smartapi._id
    smartapi.url
    smartapi.version
    ...
    """
    mygene = SmartAPI.get(MYGENE_ID)
    assert mygene._id == MYGENE_ID
    assert mygene.version == 'openapi'
    assert mygene.username == 'tester'
    assert mygene.slug == 'mygene'
    assert mygene['info']['title'] == 'MyGene.info API'
    assert mygene.raw == MYGENE_RAW
    assert mygene.url == MYGENE_URL

    with pytest.raises(AttributeError):
        mygene._id = "NEWID"
    with pytest.raises(AttributeError):
        mygene.url = "http://example.org/"
    with pytest.raises(ValueError):
        mygene.slug = "a"
    with pytest.raises(ValueError):
        mygene.slug = "AAA"
    with pytest.raises(ValueError):
        mygene.slug = "www"
    with pytest.raises(ValueError):
        mygene.slug = "^_^"

    with pytest.raises(NotFoundError):
        SmartAPI.get("NOTEXIST")


def test_get_tags():
    """
    SmartAPI.get_tags()
    SmartAPI.get_tags(field)
    """
    aggs = SmartAPI.get_tags()
    assert aggs == {'Chunlei Wu': 2}
    aggs = SmartAPI.get_tags('tags.name')
    assert 'annotation' in aggs
    assert 'translator' in aggs
    assert 'biothings' in aggs


def test_search():
    """
    SmartAPI.exists(_id)
    SmartAPI.find(slug)
    SmartAPI.find(val, field)
    """
    assert SmartAPI.exists(MYGENE_ID)
    assert SmartAPI.exists(MYCHEM_ID)
    assert SmartAPI.find('mygene') == MYGENE_ID
    assert SmartAPI.find('mychem') == MYCHEM_ID
    assert SmartAPI.find('tester', 'username')
    assert SmartAPI.find('gene', 'tags.name') == MYGENE_ID
    assert SmartAPI.find('drug', 'tags.name') == MYCHEM_ID
    assert SmartAPI.find(MYGENE_URL, 'url') == MYGENE_ID
    assert SmartAPI.find(MYCHEM_URL, 'url') == MYCHEM_ID


def test_validation():
    """
    smartapi.validate()
    """
    URL = "http://example.com/invalid.json"
    with open(os.path.join(dirname, './validate/openapi-pass.json'), 'rb') as file:
        smartapi = SmartAPI(URL)
        smartapi.raw = file.read()
        smartapi.validate()
    with open(os.path.join(dirname, './validate/swagger-pass.json'), 'rb') as file:
        smartapi = SmartAPI(URL)
        smartapi.raw = file.read()
        smartapi.validate()
    with open(os.path.join(dirname, './validate/x-translator-pass.json'), 'rb') as file:
        smartapi = SmartAPI(URL)
        smartapi.raw = file.read()
        smartapi.validate()
    with open(os.path.join(dirname, './validate/x-translator-fail-1.yml'), 'rb') as file:
        smartapi = SmartAPI(URL)
        smartapi.raw = file.read()
        with pytest.raises(ControllerError):
            smartapi.validate()
    with open(os.path.join(dirname, './validate/x-translator-fail-2.yml'), 'rb') as file:
        smartapi = SmartAPI(URL)
        smartapi.raw = file.read()
        with pytest.raises(ControllerError):
            smartapi.validate()
    smartapi = SmartAPI(URL)
    smartapi.raw = b'{}'
    with pytest.raises(ControllerError):
        smartapi.validate()


@pytest.fixture
def openapi():
    yield '5f5141cbae5ca099d3f420f9c42c94cf'
    refresh()
    try:  # teardown
        APIDoc.get('5f5141cbae5ca099d3f420f9c42c94cf').delete()
    except elasticsearch.exceptions.NotFoundError:
        pass


def test_save(openapi):
    """
    SmartAPI.slug.validate(slug)
    smartapi.slug
    smartapi.save()
    """
    URL = "http://example.com/valid.json"
    with pytest.raises(ValueError):
        SmartAPI.slug.validate("a")
    with pytest.raises(ValueError):
        SmartAPI.slug.validate("AAA")
    with pytest.raises(ValueError):
        SmartAPI.slug.validate("www")
    with pytest.raises(ValueError):
        SmartAPI.slug.validate("^_^")
    with open(os.path.join(dirname, './validate/openapi-pass.json'), 'rb') as file:
        raw = file.read()
        smartapi = SmartAPI(URL)
        smartapi.raw = raw
        smartapi.slug = "mygene"
        smartapi.validate()
        with pytest.raises(ControllerError):
            smartapi.save()
        smartapi.username = "tester"
        with pytest.raises(ConflictError):
            smartapi.save()
        smartapi.slug = "mychem"
        with pytest.raises(ConflictError):
            smartapi.save()
        smartapi.slug = "openapi"
        smartapi.raw = None
        with pytest.raises(ControllerError):
            smartapi.save()
        smartapi.raw = raw
        smartapi.save()
        refresh()
        assert SmartAPI.find("openapi") == smartapi._id
        smartapi.save()  # no change
        refresh()
        assert SmartAPI.find("openapi") == smartapi._id
        smartapi.slug = None
        smartapi.save()
        refresh()
        assert not SmartAPI.find("openapi")
        found = SmartAPI.get(openapi)
        assert dict(smartapi) == dict(found)
        assert smartapi.username == found.username
        assert smartapi.slug == found.slug
        assert smartapi.url == found.url


@pytest.fixture
def myvariant():

    with open(os.path.join(dirname, 'myvariant.es.json'), 'r') as file:
        MYVARIANT_ES = json.load(file)
    with open(os.path.join(dirname, 'myvariant.yml'), 'rb') as file:
        MYVARIANT_RAW = file.read()
    MYVARIANT_ID = MYVARIANT_ES.pop("_id")

    myvariant = APIDoc(meta={'id': MYVARIANT_ID}, **MYVARIANT_ES)
    myvariant._raw = decoder.compress(MYVARIANT_RAW)
    myvariant.save()

    refresh()
    yield MYVARIANT_ID
    refresh()

    try:
        APIDoc.get(MYVARIANT_ID).delete()
    except elasticsearch.exceptions.NotFoundError:
        pass


def test_delete(myvariant):

    mv = SmartAPI.get(myvariant)
    mv.delete()

    refresh()

    assert not APIDoc.exists(myvariant)

    URL = "http://example.com/valid.json"
    with open(os.path.join(dirname, './validate/openapi-pass.json'), 'rb') as file:
        smartapi = SmartAPI(URL)
        smartapi.raw = file.read()
        with pytest.raises(NotFoundError):
            smartapi.delete()


def test_uptime_status():
    mygene = SmartAPI.get(MYGENE_ID)
    assert mygene.uptime.status is None

    mygene.uptime.update('up')
    assert mygene.uptime.status == 'up'
    mygene.save()
    refresh()
    mygene_doc = APIDoc.get(MYGENE_ID)
    assert mygene_doc._stat.uptime_status == 'up'

    mygene.uptime.update(None)
    assert mygene.uptime.status is None
    mygene.save()
    refresh()
    mygene_doc = APIDoc.get(MYGENE_ID)
    assert mygene_doc._stat.uptime_status is None


def test_uptime_update():
    mygene = SmartAPI.get(MYGENE_ID)
    mygene.check()  # minimum api document
    assert mygene.uptime.status == 'incompatible'

    mygene.save()
    refresh()

    mygene_doc = APIDoc.get(MYGENE_ID)
    assert mygene_doc._stat.uptime_status == 'incompatible'

    mychem = SmartAPI.get(MYCHEM_ID)
    mychem.check()  # full api document
    assert mychem.uptime.status == 'good'

    mychem.save()
    refresh()

    mychem_doc = APIDoc.get(MYCHEM_ID)
    assert mychem_doc._stat.uptime_status == 'good'


def test_refresh_status():

    with open(os.path.join(dirname, 'mygene_full.yml'), 'rb') as file:
        MYGENE_FULL = file.read()

    mygene = SmartAPI.get(MYGENE_ID)  # minimum
    assert mygene.webdoc.status is None
    assert 'components' not in mygene

    mygene.webdoc.update(File(200, MYGENE_FULL))  # new content

    assert mygene.webdoc.status == 299  # updated
    assert 'components' in mygene
    assert mygene.webdoc.timestamp > datetime(2020, 1, 1)
    _ts0 = mygene.webdoc.timestamp

    mygene.save()
    refresh()

    mygene_doc = APIDoc.get(MYGENE_ID)
    assert mygene_doc._stat.refresh_status == 299
    assert 'components' in mygene_doc

    mygene.webdoc.update(File(200, MYGENE_FULL))  # no change

    assert mygene.webdoc.status == 200  # latest
    assert 'components' in mygene
    assert mygene.webdoc.timestamp > _ts0

    mygene.save()
    refresh()

    mygene_doc = APIDoc.get(MYGENE_ID)
    assert mygene_doc._stat.refresh_status == 200
    assert 'components' in mygene_doc

    mygene.webdoc.update(File(404))  # link broken

    assert mygene.webdoc.status == 404
    assert 'components' in mygene  # do not affect main copy

    mygene.save()
    refresh()

    mygene_doc = APIDoc.get(MYGENE_ID)
    assert mygene_doc._stat.refresh_status == 404
    assert 'components' in mygene_doc

    mygene.webdoc.update(File(200, MYGENE_FULL))  # link back working

    assert mygene.webdoc.status == 200  # latest
    assert 'components' in mygene

    mygene.save()
    refresh()

    mygene_doc = APIDoc.get(MYGENE_ID)
    assert mygene_doc._stat.refresh_status == 200
    assert 'components' in mygene_doc

    mygene.webdoc.update(File(200, b'{"openapi":"3.0.0"}'))  # invalid

    assert mygene.webdoc.status == 499  # invalid
    assert 'components' in mygene  # do not affect main copy

    mygene.save()
    refresh()

    mygene_doc = APIDoc.get(MYGENE_ID)
    assert mygene_doc._stat.refresh_status == 499
    assert 'components' in mygene_doc


def test_refresh_update():

    mychem = SmartAPI.get(MYCHEM_ID)
    assert mychem.webdoc.status is None

    # NOTE
    # the following update and the updates thereafter will be applied
    # https://github.com/NCATS-Tangerine/translator-api-registry/commit/b01baa5

    mychem.refresh()
    assert mychem.webdoc.status == 299  # new version
    assert mychem.webdoc.timestamp > datetime(2020, 1, 1, tzinfo=timezone.utc)
    _ts0 = mychem.webdoc.timestamp

    mychem.refresh()
    assert mychem.webdoc.status == 200  # already latest
    assert mychem.webdoc.timestamp >= _ts0  # could be cached internally

    mychem.save()
    refresh()
    mychem_doc = APIDoc.get(MYCHEM_ID)
    assert mychem_doc._stat.refresh_status == 200
