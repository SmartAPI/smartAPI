"""
SmartAPI Controller Tests
"""
import json
import os
import time
from datetime import datetime, timedelta, timezone

import elasticsearch
import pytest
from controller.exceptions import ConflictError, ControllerError, NotFoundError
from controller.smartapi import SmartAPI
from model import SmartAPIDoc
from utils import decoder
from utils.downloader import File
from utils.indices import delete, refresh, reset

ES_INDEX_NAME = "smartapi_docs_test"

MYGENE_URL = (
    "https://raw.githubusercontent.com/NCATS-Tangerine/translator-api-registry/master/mygene.info/openapi_minimum.yml"
)
MYCHEM_URL = (
    "https://raw.githubusercontent.com/NCATS-Tangerine/translator-api-registry/master/mychem.info/openapi_full.yml"
)

# MYGENE_ID = "67932b75e2c51d1e1da2bf8263e59f0a"
# MYCHEM_ID = "8f08d1446e0bb9c2b323713ce83e2bd3"

dirname = os.path.dirname(__file__)

# prepare data to be saved in tests
with open(os.path.join(dirname, "mygene.es.json"), "r") as file:
    MYGENE_ES = json.load(file)

with open(os.path.join(dirname, "mychem.es.json"), "r") as file:
    MYCHEM_ES = json.load(file)

with open(os.path.join(dirname, "mygene.yml"), "rb") as file:
    MYGENE_RAW = file.read()

with open(os.path.join(dirname, "mychem.yml"), "rb") as file:
    MYCHEM_RAW = file.read()

MYGENE_ID = MYGENE_ES.pop("_id")
MYCHEM_ID = MYCHEM_ES.pop("_id")


@pytest.fixture(scope="module", autouse=True)
def setup_fixture():
    """
    Index 2 documents.
    """
    SmartAPI.INDEX = ES_INDEX_NAME
    reset(SmartAPI.MODEL_CLASS, index=ES_INDEX_NAME)
    # save initial docs with paths already transformed
    mygene = SmartAPIDoc(meta={"id": MYGENE_ID}, **MYGENE_ES)
    mygene._raw = decoder.compress(MYGENE_RAW)
    mygene.save(index=ES_INDEX_NAME)

    mychem = SmartAPIDoc(meta={"id": MYCHEM_ID}, **MYCHEM_ES)
    mychem._raw = decoder.compress(MYCHEM_RAW)
    mychem.save(index=ES_INDEX_NAME)

    # refresh index
    refresh(index=ES_INDEX_NAME)


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
    search = SmartAPIDoc.search(index=ES_INDEX_NAME)
    assert search.count() == 2

    docs = list(SmartAPI.get_all(size=1))
    assert len(docs) == 1


def test_get_all_from():
    """
    SmartAPI.get_all(from_=1)
    """
    search = SmartAPIDoc.search(index=ES_INDEX_NAME)
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
    assert mygene.version == "openapi"
    assert mygene.username == "tester"
    assert mygene.slug == "mygene"
    assert mygene["info"]["title"] == "MyGene.info API"
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
    assert aggs == {"Chunlei Wu": 2}
    aggs = SmartAPI.get_tags("tags.name")
    assert "annotation" in aggs
    assert "translator" in aggs
    assert "biothings" in aggs


def test_search():
    """
    SmartAPI.exists(_id)
    SmartAPI.find(slug)
    SmartAPI.find(val, field)
    """
    assert SmartAPI.exists(MYGENE_ID)
    assert SmartAPI.exists(MYCHEM_ID)
    assert SmartAPI.find("mygene") == MYGENE_ID
    assert SmartAPI.find("mychem") == MYCHEM_ID
    assert SmartAPI.find("tester", "username")
    assert SmartAPI.find("gene", "tags.name") == MYGENE_ID
    assert SmartAPI.find("drug", "tags.name") == MYCHEM_ID
    assert SmartAPI.find(MYGENE_URL, "url") == MYGENE_ID
    assert SmartAPI.find(MYCHEM_URL, "url") == MYCHEM_ID


def test_validation():
    """
    smartapi.validate()
    """
    URL = "http://example.com/invalid.json"
    with open(os.path.join(dirname, "./validate/openapi-pass.json"), "rb") as file:
        smartapi = SmartAPI(URL)
        smartapi.raw = file.read()
        smartapi.validate()
    with open(os.path.join(dirname, "./validate/swagger-pass.json"), "rb") as file:
        smartapi = SmartAPI(URL)
        smartapi.raw = file.read()
        smartapi.validate()
    with open(os.path.join(dirname, "./validate/x-translator-pass.json"), "rb") as file:
        smartapi = SmartAPI(URL)
        smartapi.raw = file.read()
        smartapi.validate()
    with open(os.path.join(dirname, "./validate/x-translator-fail-1.yml"), "rb") as file:
        smartapi = SmartAPI(URL)
        smartapi.raw = file.read()
        with pytest.raises(ControllerError):
            smartapi.validate()
    with open(os.path.join(dirname, "./validate/x-translator-fail-2.yml"), "rb") as file:
        smartapi = SmartAPI(URL)
        smartapi.raw = file.read()
        with pytest.raises(ControllerError):
            smartapi.validate()
    smartapi = SmartAPI(URL)
    smartapi.raw = b"{}"
    with pytest.raises(ControllerError):
        smartapi.validate()


@pytest.fixture
def openapi():
    yield "5f5141cbae5ca099d3f420f9c42c94cf"
    refresh(index=ES_INDEX_NAME)
    try:  # teardown
        SmartAPIDoc.get("5f5141cbae5ca099d3f420f9c42c94cf", index=ES_INDEX_NAME).delete()
    except elasticsearch.exceptions.NotFoundError:
        pass


def test_save(openapi):
    """
    SmartAPI.slug.validate(slug)
    smartapi.slug
    smartapi.save()
    """
    _t0 = datetime.now(timezone.utc)
    time.sleep(0.1)
    URL = "http://example.com/valid.json"
    with pytest.raises(ValueError):
        SmartAPI.slug.validate("a")
    with pytest.raises(ValueError):
        SmartAPI.slug.validate("AAA")
    with pytest.raises(ValueError):
        SmartAPI.slug.validate("www")
    with pytest.raises(ValueError):
        SmartAPI.slug.validate("^_^")
    with open(os.path.join(dirname, "./validate/openapi-pass.json"), "rb") as file:
        raw = file.read()
        smartapi = SmartAPI(URL)
        with pytest.raises(ControllerError):
            smartapi.raw = None
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
        smartapi.save()
        refresh(index=ES_INDEX_NAME)
        assert SmartAPI.find("openapi") == smartapi._id
        assert smartapi.date_created > _t0
        assert smartapi.last_updated > _t0
        assert smartapi.date_created == smartapi.last_updated
        apidoc = SmartAPIDoc.get(smartapi._id, index=ES_INDEX_NAME)
        assert apidoc._meta.date_created == smartapi.date_created
        assert apidoc._meta.last_updated == smartapi.last_updated
        _t1 = smartapi.date_created
        smartapi.save()  # no change
        refresh(index=ES_INDEX_NAME)
        assert SmartAPI.find("openapi") == smartapi._id
        assert smartapi.date_created == _t1
        assert smartapi.last_updated == _t1
        assert smartapi.date_created == smartapi.last_updated
        apidoc = SmartAPIDoc.get(smartapi._id, index=ES_INDEX_NAME)
        assert apidoc._meta.date_created == smartapi.date_created
        assert apidoc._meta.last_updated == smartapi.last_updated
        smartapi.slug = None
        smartapi.save()
        refresh(index=ES_INDEX_NAME)
        assert not SmartAPI.find("openapi")
        found = SmartAPI.get(openapi)
        assert dict(smartapi) == dict(found)
        assert smartapi.username == found.username
        assert smartapi.slug == found.slug
        assert smartapi.url == found.url
        assert smartapi.date_created == _t1
        assert smartapi.last_updated == _t1
        assert smartapi.date_created == smartapi.last_updated
        apidoc = SmartAPIDoc.get(smartapi._id, index=ES_INDEX_NAME)
        assert apidoc._meta.date_created == smartapi.date_created
        assert apidoc._meta.last_updated == smartapi.last_updated
        smartapi.raw = raw  # should trigger ts update
        smartapi.save()
        refresh(index=ES_INDEX_NAME)
        assert smartapi.date_created == _t1
        assert smartapi.last_updated > _t1
        apidoc = SmartAPIDoc.get(smartapi._id, index=ES_INDEX_NAME)
        assert apidoc._meta.date_created == smartapi.date_created
        assert apidoc._meta.last_updated == smartapi.last_updated


@pytest.fixture
def myvariant():
    with open(os.path.join(dirname, "myvariant.es.json"), "r") as file:
        MYVARIANT_ES = json.load(file)
    with open(os.path.join(dirname, "myvariant.yml"), "rb") as file:
        MYVARIANT_RAW = file.read()
    MYVARIANT_ID = MYVARIANT_ES.pop("_id")

    myvariant = SmartAPIDoc(meta={"id": MYVARIANT_ID}, **MYVARIANT_ES)
    myvariant._raw = decoder.compress(MYVARIANT_RAW)
    myvariant.save(index=ES_INDEX_NAME)

    refresh(index=ES_INDEX_NAME)
    yield MYVARIANT_ID
    refresh(index=ES_INDEX_NAME)

    try:
        SmartAPIDoc.get(MYVARIANT_ID, index=ES_INDEX_NAME).delete()
    except elasticsearch.exceptions.NotFoundError:
        pass


def test_delete(myvariant):
    mv = SmartAPI.get(myvariant)
    mv.delete()

    refresh(index=ES_INDEX_NAME)

    assert not SmartAPIDoc.exists(myvariant, index=ES_INDEX_NAME)

    URL = "http://example.com/valid.json"
    with open(os.path.join(dirname, "./validate/openapi-pass.json"), "rb") as file:
        smartapi = SmartAPI(URL)
        smartapi.raw = file.read()
        with pytest.raises(NotFoundError):
            smartapi.delete()


def test_uptime_status():
    mygene = SmartAPI.get(MYGENE_ID)
    assert mygene.uptime.status[0] is None

    mygene.uptime.update(("pass", None))
    assert mygene.uptime.status[0] == "pass"
    mygene.save()
    refresh(index=ES_INDEX_NAME)
    mygene_doc = SmartAPIDoc.get(MYGENE_ID, index=ES_INDEX_NAME)
    assert mygene_doc._status.uptime_status == "pass"

    mygene.uptime.update((None, None))
    assert mygene.uptime.status[0] is None
    mygene.save()
    refresh(index=ES_INDEX_NAME)
    mygene_doc = SmartAPIDoc.get(MYGENE_ID, index=ES_INDEX_NAME)
    assert mygene_doc._status.uptime_status is None


# @pytest.mark.skip("This test is failed, due to the chem endpoint requires id must be set")
def test_uptime_update():
    mygene = SmartAPI.get(MYGENE_ID)
    mygene.check()  # minimum api document
    assert mygene.uptime.status[0] == "unknown"  # TODO VERIFY THIS IS IN FACT CORRECT

    mygene.save()
    refresh(index=ES_INDEX_NAME)

    mygene_doc = SmartAPIDoc.get(MYGENE_ID, index=ES_INDEX_NAME)
    assert mygene_doc._status.uptime_status == "unknown"

    mychem = SmartAPI.get(MYCHEM_ID)
    mychem.check()  # full api document
    # NOTE: fail here. The request data must contains id
    # mychem.check() => {/chem: (400) {"code":400,"success":false,"error":"Bad Request","missing":"id","alias":"ids"}
    assert mychem.uptime.status[0] == "fail"

    mychem.save()
    refresh(index=ES_INDEX_NAME)

    mychem_doc = SmartAPIDoc.get(MYCHEM_ID, index=ES_INDEX_NAME)
    assert mychem_doc._status.uptime_status == "fail"


def test_refresh_status():
    with open(os.path.join(dirname, "mygene_full.yml"), "rb") as file:
        MYGENE_FULL = file.read()

    mygene = SmartAPI.get(MYGENE_ID)  # minimum
    assert mygene.webdoc.status is None
    assert "components" not in mygene

    mygene.webdoc.update(File(200, MYGENE_FULL, None, None))  # new content

    assert mygene.webdoc.status == 299  # updated
    assert "components" in mygene
    assert mygene.webdoc.timestamp > datetime(2020, 1, 1).astimezone()
    _ts0 = mygene.webdoc.timestamp

    original_last_updated = mygene.last_updated.replace(microsecond=0, tzinfo=timezone.utc)
    one_hour_before = (datetime.now(timezone.utc) - timedelta(hours=1)).replace(microsecond=0)
    assert original_last_updated > one_hour_before

    mygene.save()
    refresh(index=ES_INDEX_NAME)

    mygene_doc = SmartAPIDoc.get(MYGENE_ID, index=ES_INDEX_NAME)
    assert mygene_doc._status.refresh_status == 299
    assert "components" in mygene_doc

    mygene.webdoc.update(File(200, MYGENE_FULL, None, None))  # no change

    assert mygene.webdoc.status == 200  # latest
    assert "components" in mygene
    assert mygene.webdoc.timestamp > _ts0

    current_last_updated = mygene.last_updated.replace(microsecond=0, tzinfo=timezone.utc)
    assert current_last_updated == original_last_updated

    mygene.save()
    refresh(index=ES_INDEX_NAME)

    # confirm last_updated is not changed after refresh
    assert mygene.last_updated.replace(microsecond=0, tzinfo=timezone.utc) == current_last_updated

    mygene_doc = SmartAPIDoc.get(MYGENE_ID, index=ES_INDEX_NAME)
    assert mygene_doc._status.refresh_status == 200
    assert "components" in mygene_doc

    mygene.webdoc.update(File(404, None, None, None))  # link broken

    assert mygene.webdoc.status == 404
    assert "components" in mygene  # do not affect main copy

    mygene.save()
    refresh(index=ES_INDEX_NAME)

    # confirm last_updated is not changed after refresh
    assert mygene.last_updated.replace(microsecond=0, tzinfo=timezone.utc) == current_last_updated

    mygene_doc = SmartAPIDoc.get(MYGENE_ID, index=ES_INDEX_NAME)
    assert mygene_doc._status.refresh_status == 404
    assert "components" in mygene_doc

    mygene.webdoc.update(File(200, MYGENE_FULL, None, None))  # link back working

    assert mygene.webdoc.status == 200  # latest
    assert "components" in mygene

    mygene.save()
    refresh(index=ES_INDEX_NAME)

    mygene_doc = SmartAPIDoc.get(MYGENE_ID, index=ES_INDEX_NAME)
    assert mygene_doc._status.refresh_status == 200
    assert "components" in mygene_doc

    mygene.webdoc.update(File(200, b'{"openapi":"3.0.0"}', None, None))  # invalid

    assert mygene.webdoc.status == 499  # invalid
    assert "components" in mygene  # do not affect main copy

    mygene.save()
    refresh(index=ES_INDEX_NAME)

    # confirm last_updated is not changed after refresh
    assert mygene.last_updated.replace(microsecond=0, tzinfo=timezone.utc) == current_last_updated

    mygene_doc = SmartAPIDoc.get(MYGENE_ID, index=ES_INDEX_NAME)
    assert mygene_doc._status.refresh_status == 499
    assert "components" in mygene_doc


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
    refresh(index=ES_INDEX_NAME)
    mychem_doc = SmartAPIDoc.get(MYCHEM_ID, index=ES_INDEX_NAME)
    assert mychem_doc._status.refresh_status == 200


def teardown_module():
    delete(SmartAPI.MODEL_CLASS, index=SmartAPI.INDEX)
    SmartAPI.INDEX = None
