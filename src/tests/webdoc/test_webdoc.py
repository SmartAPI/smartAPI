import os
from datetime import datetime

import pytest
from controller import APIWebDoc, ControllerError, NotFoundError
from model import APIMeta
from utils import decoder, indices
from utils.downloader import File

dirname = os.path.dirname(__file__)


with open(os.path.join(dirname, 'mydisease.yaml'), 'rb') as file:
    MYDIS = file.read()

with open(os.path.join(dirname, 'myvariant.yml'), 'rb') as file:
    MYVAR = file.read()

MYVAR_URL = "http://example.com/test/myvariant.yml"  # Fake url used for testing


@pytest.fixture()
def with_mydisease():
    indices.refresh()

    mydis = APIMeta()
    mydis.meta.id = "df519c0867a85755e21cbe9e01f136b9"
    mydis.url = "http://example.com/test/mydisease.yaml"  # Fake url used for testing
    mydis.web_status = 200
    mydis.web_etag = "58fd3590a74f809cc50e34f462977901b06ed423d19f8a498229e36d916d4bd0"
    mydis.web_raw = decoder.compress(MYDIS)
    mydis.web_ts = datetime(1900, 1, 1, 0, 0)
    mydis.uptime_status = "good"
    mydis.uptime_ts = datetime(1900, 1, 1, 0, 0)
    mydis.save()

    indices.refresh()
    return mydis.meta.id


@pytest.fixture()
def without_myvariant():
    indices.refresh()

    _id = APIMeta.exists(MYVAR_URL, "url")
    if _id:
        APIMeta.get(_id).delete()

    indices.refresh()


def test_get(with_mydisease):

    with pytest.raises(NotFoundError):
        APIWebDoc.get("__404__")

    doc = APIWebDoc.get(_id=with_mydisease)
    assert set(doc.keys()) == {'components', 'tags', 'paths', 'openapi', 'servers', 'info'}
    assert doc.etag == "58fd3590a74f809cc50e34f462977901b06ed423d19f8a498229e36d916d4bd0"
    assert doc.timestamp == datetime(1900, 1, 1, 0, 0)
    assert doc.status == 200
    assert doc.raw == MYDIS


def test_delete(with_mydisease):

    with pytest.raises(ControllerError):
        doc = APIWebDoc.get(_id=with_mydisease)
        doc.delete()  # Not Allowed


def test_create(without_myvariant):

    doc = APIWebDoc(MYVAR_URL)
    doc.raw = MYVAR
    doc.save()

    indices.refresh()

    _id = APIMeta.exists(MYVAR_URL, "url")
    assert _id
    meta = APIMeta.get(_id)
    assert decoder.decompress(meta.web_raw) == MYVAR
    assert meta.url == MYVAR_URL


def test_update(with_mydisease):

    mydis = APIWebDoc.get(_id=with_mydisease)
    mydis.etag = "MODIFIED_NEW_VALUE"
    mydis.refresh_timestamp()
    mydis.save()

    indices.refresh()

    meta = APIMeta.get(id=with_mydisease)
    assert meta.web_status == 200  # not modified
    assert meta.web_etag == "MODIFIED_NEW_VALUE"
    assert meta.web_raw == decoder.compress(MYDIS)  # not modified
    assert meta.web_ts > datetime(1900, 1, 1, 0, 0)
    assert meta.uptime_status == "good"  # not modified
    assert meta.uptime_ts == datetime(1900, 1, 1, 0, 0)  # not modified


def test_refresh(with_mydisease):

    mydis = APIWebDoc.get(_id=with_mydisease)
    mydis.refresh(File(404, date=datetime.utcnow()))
    mydis.save()

    indices.refresh()

    meta = APIMeta.get(id=with_mydisease)
    assert meta.web_status == 404
    assert meta.web_etag is None
    assert meta.web_raw is None
    assert meta.web_ts > datetime(1900, 1, 1, 0, 0)
    assert meta.uptime_status == "good"  # not modified
    assert meta.uptime_ts == datetime(1900, 1, 1, 0, 0)  # not modified
