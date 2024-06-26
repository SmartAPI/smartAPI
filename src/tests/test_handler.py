"""
    SmartAPI Tornado Handler Tests

    Setup:
        mygene_minimum
        mychem_full

    CRUD Testcases:

        read mygene
        read mychem
        read all

        add lincs

        refresh mychem (with live content change)
        refresh mygene (simulate url broken)

        update mygene slug
        delete mygene

    Note: Cannot directly combine pytest class fixture with tornado test class.
    Some teardown code are in the testcases and may be skipped if the testcase failed.

"""

import json
import os

import pytest
import tornado
import yaml
from biothings.tests.web import BiothingsTestCase
from tornado.escape import json_encode
from tornado.web import create_signed_value

from controller.exceptions import NotFoundError
from controller.smartapi import SmartAPI
from model import SmartAPIDoc
from utils import decoder
from utils.indices import refresh, reset

MYGENE_URL = (
    "https://raw.githubusercontent.com/NCATS-Tangerine/translator-api-registry/master/mygene.info/openapi_minimum.yml"
)
MYCHEM_URL = (
    "https://raw.githubusercontent.com/NCATS-Tangerine/translator-api-registry/master/mychem.info/openapi_full.yml"
)

MYGENE_ID = "59dce17363dce279d389100834e43648"
MYCHEM_ID = "8f08d1446e0bb9c2b323713ce83e2bd3"


dirname = os.path.dirname(__file__)

# prepare data to be saved in tests
with open(os.path.join(dirname, "mygene.es.json"), "r") as file:
    MYGENE_ES = json.load(file)
    MYGENE_ID = MYGENE_ES.pop("_id")


with open(os.path.join(dirname, "mychem.es.json"), "r") as file:
    MYCHEM_ES = json.load(file)
    MYCHEM_ID = MYCHEM_ES.pop("_id")


with open(os.path.join(dirname, "mygene.yml"), "rb") as file:
    MYGENE_RAW = file.read()

with open(os.path.join(dirname, "mychem.yml"), "rb") as file:
    MYCHEM_RAW = file.read()


@pytest.fixture(autouse=True, scope="module")
def setup_fixture():
    """
    Index 2 documents.
    """
    test_index = "smartapi_docs_test"
    os.environ['SMARTAPI_ES_INDEX'] = test_index
    
    print(os.environ['SMARTAPI_ES_INDEX'])

    reset(index_name=test_index)

    # save initial docs with paths already transformed
    mygene = SmartAPI(MYGENE_URL)
    mygene.raw = MYGENE_RAW
    mygene.username = "tester"
    mygene.slug = "mygene"
    mygene.save(index=test_index, test_mode=True)

    mychem = SmartAPI(MYCHEM_URL)
    mychem.raw = MYCHEM_RAW
    mychem.username = "tester"
    mychem.slug = "mychem"
    mychem.save(index=test_index, test_mode=True)

    refresh(index_name=test_index)


class SmartAPIEndpoint(BiothingsTestCase):
    @classmethod
    def cookie_header(cls, username):
        cookie_name, cookie_value = "user", {"login": username}
        # NOTE: this statement causes an error, due to no settings can found in SmartAPIEndpoint
        secure_cookie = create_signed_value(cls.settings.COOKIE_SECRET, cookie_name, json_encode(cookie_value))
        return {"Cookie": "=".join((cookie_name, secure_cookie.decode()))}

    @property
    def auth_user(self):
        return self.cookie_header("tester")

    @property
    def evil_user(self):
        return self.cookie_header("eviluser01")

    def get_app(self):
        app = super().get_app()
        app.settings["debug"] = True
        return app


class TestValidate(SmartAPIEndpoint):
    # TODO
    # URL TEST MOVES TO LOCAL SERVER

    def test_url_valid(self):
        """
        [POST] with url
        """
        VALID_V3_URL = (
            "https://raw.githubusercontent.com/schurerlab/" "smartAPIs/master/LINCS_Data_Portal_smartAPIs.yml"
        )

        self.request("/api/validate/", method="POST", data={"url": VALID_V3_URL})

    @pytest.mark.skip("The url for testing is valid. Should we change to another?")
    def test_url_invalid(self):
        """
        [POST] with url of invalid data
        """
        INVALID_V3_URL = "https://raw.githubusercontent.com/marcodarko/" "api_exmaple/master/api.yml"

        self.request("/api/validate/", method="POST", data={"url": INVALID_V3_URL}, expect=400)

    def test_json(self):
        """
        [POST] with JSON body
        """
        headers = {"Content-type": "application/yaml", "Accept": "text/plain"}
        self.request("/api/validate/", method="POST", json=decoder.to_dict(MYGENE_RAW))
        self.request("/api/validate/", method="POST", data=MYGENE_RAW, headers=headers)
        self.request("/api/validate/", method="POST", data=MYGENE_RAW)
        with open(os.path.join(dirname, "./validate/openapi-pass.json"), "rb") as file:
            self.request("/api/validate/", method="POST", data=file.read())
        with open(os.path.join(dirname, "./validate/swagger-pass.json"), "rb") as file:
            self.request("/api/validate/", method="POST", data=file.read())
        with open(os.path.join(dirname, "./validate/x-translator-pass.json"), "rb") as file:
            self.request("/api/validate/", method="POST", data=file.read())
        with open(os.path.join(dirname, "./validate/x-translator-fail-1.yml"), "rb") as file:
            self.request("/api/validate/", method="POST", data=file.read(), expect=400)
        with open(os.path.join(dirname, "./validate/x-translator-fail-2.yml"), "rb") as file:
            self.request("/api/validate/", method="POST", data=file.read(), expect=400)


class TestSuggestion(SmartAPIEndpoint):
    def test_suggestion(self):
        """
        [GET] get aggregations for field
        """
        self.request("/api/suggestion", expect=400)
        res = self.request("/api/suggestion?field=tags.name").json()
        assert "annotation" in res
        assert res["annotation"] == 2
        assert "translator" in res
        assert res["translator"] == 2


class DynamicFileHandler(tornado.web.StaticFileHandler):
    counter = 0

    @classmethod
    def get_absolute_path(cls, root: str, path: str) -> str:
        if path == "mygene.yml":
            if cls.counter == 0:
                pass
            elif cls.counter == 1:
                path = "mygene_full.yml"
            elif cls.counter == 2:
                path = "mygene_notexist.yml"
            elif cls.counter == 3:
                path = "mygene_invalid.yml"  # no translator info
            else:
                path = "mygene_full.yml"
            cls.counter += 1

        abspath = os.path.abspath(os.path.join(root, path))
        return abspath


@pytest.mark.skip("All tests failed by TestCRUD has no attribute: settings")
class TestCRUD(SmartAPIEndpoint):
    def get_app(self):
        return tornado.web.Application(
            [
                (r"/test/(.*)", DynamicFileHandler, {"path": "./tests/"}),  # cwd is project src
                (r".*", super().get_app()),
            ]
        )

    def test_get_one(self):
        res = self.request("/api/metadata/" + MYGENE_ID).json()
        assert res.get("info", {}).get("title", "") == "MyGene.info API"

        res = self.request("/api/metadata/" + MYCHEM_ID).json()
        assert res.get("info", {}).get("title", "") == "MyChem.info API"

        res = self.request("/api/metadata/" + MYGENE_ID + "?format=yaml")
        yaml.load(res.text, Loader=yaml.SafeLoader)

    def test_get_all(self):
        res = self.request("/api/metadata/", method="GET").json()
        assert len(res) == 2

        res = self.request("/api/metadata?from_=1", method="GET").json()
        assert len(res) == 1

        res = self.request("/api/metadata?size=1", method="GET").json()
        assert len(res) == 1

    def test_post(self):
        _ID = "1ad2cba40cb25cd70d00aa8fba9cfaf3"
        VALID_V3_URL = (
            "https://raw.githubusercontent.com/schurerlab/" "smartAPIs/master/LINCS_Data_Portal_smartAPIs.yml"
        )

        try:
            smartapi = SmartAPI.get(_ID)
            smartapi.delete()
            refresh()
        except NotFoundError:
            pass

        self.request("/api/metadata/", method="POST", data={"url": VALID_V3_URL}, expect=401)
        self.request("/api/metadata/", method="POST", data={"url": MYGENE_URL}, headers=self.auth_user, expect=409)
        self.request("/api/metadata/", method="POST", headers=self.auth_user, expect=400)
        self.request(
            "/api/metadata/", method="POST", data={"url": "http://invalidhost/file"}, headers=self.auth_user, expect=400
        )
        self.request(
            "/api/metadata/", method="POST", data={"url": VALID_V3_URL, "dryrun": True}, headers=self.auth_user
        )
        refresh()
        assert not SmartAPI.exists(_ID)
        self.request("/api/metadata/", method="POST", data={"url": VALID_V3_URL}, headers=self.auth_user)
        refresh()
        assert SmartAPI.exists(_ID)

        try:
            smartapi = SmartAPI.get(_ID)
            smartapi.delete()
        except NotFoundError:
            pass

    def test_update_slug(self):
        mygene = SmartAPI.get(MYGENE_ID)
        assert mygene.slug == "mygene"

        self.request("/api/metadata/" + MYGENE_ID, method="PUT", data={"slug": "mygeeni"}, expect=401)
        self.request(
            "/api/metadata/" + MYGENE_ID, method="PUT", data={"slug": "mygeeni"}, headers=self.evil_user, expect=403
        )
        self.request(
            "/api/metadata/" + MYGENE_ID, method="PUT", data={"slug": "my"}, headers=self.auth_user, expect=400
        )
        self.request(
            "/api/metadata/" + MYGENE_ID, method="PUT", data={"slug": "www"}, headers=self.auth_user, expect=400
        )
        self.request(
            "/api/metadata/" + MYGENE_ID, method="PUT", data={"slug": "MYGENE"}, headers=self.auth_user, expect=400
        )
        self.request(
            "/api/metadata/" + MYGENE_ID, method="PUT", data={"slug": "mygene!!"}, headers=self.auth_user, expect=400
        )
        self.request("/api/metadata/" + MYGENE_ID, method="PUT", data={"slug": "mygeeni"}, headers=self.auth_user)

        refresh()
        assert not SmartAPI.find("mygene")
        assert SmartAPI.find("mygeeni")

        self.request("/api/metadata/" + MYGENE_ID, method="PUT", data={"slug": ""}, headers=self.auth_user)

        refresh()
        assert not SmartAPI.find("mygeeni")
        assert not SmartAPI.find("mygene")

        self.request("/api/metadata/" + MYGENE_ID, method="PUT", data={"slug": "mygene"}, headers=self.auth_user)
        refresh()
        assert not SmartAPI.find("mygeeni")
        assert SmartAPI.find("mygene")

        # teardown
        refresh()
        if not SmartAPI.find("mygene"):
            mygene = SmartAPIDoc(meta={"id": MYGENE_ID}, **MYGENE_ES)
            mygene._raw = decoder.compress(MYGENE_RAW)
            mygene.save()

    def test_update_doc(self):
        self.request("/api/metadata/" + MYCHEM_ID, method="PUT", expect=401)
        self.request("/api/metadata/notexists", method="PUT", headers=self.auth_user, expect=404)
        self.request("/api/metadata/" + MYCHEM_ID, method="PUT", headers=self.evil_user, expect=403)

        res = self.request("/api/metadata/" + MYCHEM_ID, method="PUT", headers=self.auth_user).json()
        assert res["success"]
        assert res["code"] == 299
        assert res["status"] == "updated"

        mychem = SmartAPI.get(MYCHEM_ID)
        assert mychem.webdoc.status == 299
        assert mychem.webdoc.timestamp
        ts0 = mychem.webdoc.timestamp

        res = self.request("/api/metadata/" + MYCHEM_ID, method="PUT", headers=self.auth_user).json()
        assert res["success"]
        assert res["code"] == 200
        assert res["status"] == "not_modified"

        mychem = SmartAPI.get(MYCHEM_ID)
        assert mychem.webdoc.status == 200
        assert mychem.webdoc.timestamp >= ts0

        # setup
        mygene_ref = SmartAPI(self.get_url("/test/mygene.yml"))
        mygene_ref.raw = MYGENE_RAW
        mygene_ref.username = "tester"
        mygene_ref.save()

        # first request, same file, minimul version
        res = self.request("/api/metadata/" + mygene_ref._id, method="PUT", headers=self.auth_user).json()
        assert res["success"]
        assert res["code"] == 200
        assert res["status"] == "not_modified"

        mygene = SmartAPI.get(mygene_ref._id)
        assert mygene.webdoc.status == 200

        # second request, full version, updated
        res = self.request("/api/metadata/" + mygene_ref._id, method="PUT", headers=self.auth_user).json()
        assert res["success"]
        assert res["code"] == 299
        assert res["status"] == "updated"

        mygene = SmartAPI.get(mygene_ref._id)
        assert mygene.webdoc.status == 299

        # third request, link temporarily unavailable
        res = self.request("/api/metadata/" + mygene_ref._id, method="PUT", headers=self.auth_user).json()
        assert not res["success"]
        assert res["code"] == 404
        assert res["status"] == "nofile"

        mygene = SmartAPI.get(mygene_ref._id)
        assert mygene.webdoc.status == 404

        # fourth request, link back up, new version doesn't pass validation
        res = self.request("/api/metadata/" + mygene_ref._id, method="PUT", headers=self.auth_user).json()
        assert not res["success"]
        assert res["code"] == 499
        assert res["status"] == "invalid"

        mygene = SmartAPI.get(mygene_ref._id)
        assert mygene.webdoc.status == 499

        # fifth request, link restored to a working version
        res = self.request("/api/metadata/" + mygene_ref._id, method="PUT", headers=self.auth_user).json()
        assert res["success"]
        assert res["code"] == 200
        assert res["status"] == "not_modified"

        mygene = SmartAPI.get(mygene_ref._id)
        assert mygene.webdoc.status == 200

        # setup
        mygene_ref_2 = SmartAPI("http://invalidhost/mygene.yml")
        mygene_ref_2.raw = MYGENE_RAW
        mygene_ref_2.username = "tester"
        mygene_ref_2.save()

        res = self.request("/api/metadata/" + mygene_ref_2._id, method="PUT", headers=self.auth_user).json()
        assert not res["success"]
        assert res["code"] == 599
        assert res["status"] == "nofile"

        mygene = SmartAPI.get(mygene_ref_2._id)
        assert mygene.webdoc.status == 599

    def test_delete(self):
        # setup
        assert SmartAPI.exists(MYGENE_ID)

        self.request("/api/metadata/" + MYGENE_ID, method="DELETE", expect=401)
        self.request("/api/metadata/" + MYGENE_ID, method="DELETE", headers=self.evil_user, expect=403)
        self.request("/api/metadata/" + MYGENE_ID, method="DELETE", headers=self.auth_user)

        refresh()
        assert not SmartAPI.exists(MYGENE_ID)

        # teardown
        refresh()
        if not SmartAPI.exists(MYGENE_ID):  # recover the deleted file
            mygene = SmartAPIDoc(meta={"id": MYGENE_ID}, **MYGENE_ES)
            mygene._raw = decoder.compress(MYGENE_RAW)
            mygene.save()
        refresh()
