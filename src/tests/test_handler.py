import json
import os

import pytest
import yaml
from biothings.tests.web import BiothingsTestCase
from controller import NotFoundError, SmartAPI
from model import APIDoc
from tornado.escape import json_encode
from tornado.web import create_signed_value
from utils import decoder
from utils.indices import refresh, reset

MYGENE_URL = 'https://raw.githubusercontent.com/NCATS-Tangerine/'\
    'translator-api-registry/master/mygene.info/openapi_minimum.yml'
MYCHEM_URL = 'https://raw.githubusercontent.com/NCATS-Tangerine/'\
    'translator-api-registry/master/mychem.info/openapi_full.yml'

MYGENE_ID = '59dce17363dce279d389100834e43648'
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


class SmartAPIEndpoint(BiothingsTestCase):

    @classmethod
    def cookie_header(cls, username):
        cookie_name, cookie_value = 'user', {'login': username}
        secure_cookie = create_signed_value(
            cls.settings.COOKIE_SECRET, cookie_name,
            json_encode(cookie_value))
        return {'Cookie': '='.join((cookie_name, secure_cookie.decode()))}

    @property
    def auth_user(self):
        return self.cookie_header('tester')

    @property
    def evil_user(self):
        return self.cookie_header('eviluser01')


class TestValidate(SmartAPIEndpoint):

    # TODO
    # URL TEST MOVES TO LOCAL SERVER

    def test_url_valid(self):
        '''
        [POST] with url
        '''
        VALID_V3_URL = \
            'https://raw.githubusercontent.com/schurerlab/'\
            'smartAPIs/master/LINCS_Data_Portal_smartAPIs.yml'

        self.request(
            "/api/validate/", method='POST',
            data={'url': VALID_V3_URL}
        )

    def test_url_invalid(self):
        '''
        [POST] with url of invalid data
        '''
        INVALID_V3_URL = \
            'https://raw.githubusercontent.com/marcodarko/'\
            'api_exmaple/master/api.yml'

        self.request(
            "/api/validate/", method='POST',
            data={'url': INVALID_V3_URL}, expect=400
        )

    def test_json(self):
        '''
        [POST] with JSON body
        '''
        headers = {'Content-type': 'application/yaml', 'Accept': 'text/plain'}
        self.request("/api/validate/", method='POST', json=decoder.to_dict(MYGENE_RAW))
        self.request("/api/validate/", method='POST', data=MYGENE_RAW, headers=headers)
        self.request("/api/validate/", method='POST', data=MYGENE_RAW)
        with open(os.path.join(dirname, './validate/openapi-pass.json'), 'rb') as file:
            self.request("/api/validate/", method='POST', data=file.read())
        with open(os.path.join(dirname, './validate/swagger-pass.json'), 'rb') as file:
            self.request("/api/validate/", method='POST', data=file.read())
        with open(os.path.join(dirname, './validate/x-translator-pass.json'), 'rb') as file:
            self.request("/api/validate/", method='POST', data=file.read())
        with open(os.path.join(dirname, './validate/x-translator-fail-1.yml'), 'rb') as file:
            self.request("/api/validate/", method='POST', data=file.read(), expect=400)
        with open(os.path.join(dirname, './validate/x-translator-fail-2.yml'), 'rb') as file:
            self.request("/api/validate/", method='POST', data=file.read(), expect=400)


class TestSuggestion(SmartAPIEndpoint):

    def test_suggestion(self):
        '''
        [GET] get aggregations for field
        '''
        self.request("/api/suggestion", expect=400)
        res = self.request("/api/suggestion?field=tags.name").json()
        assert "annotation" in res
        assert res["annotation"] == 2
        assert "translator" in res
        assert res["translator"] == 2


class TestCRUD(SmartAPIEndpoint):

    def test_get_one(self):
        '''
        [READ] Get one doc by id
        '''
        res = self.request("/api/metadata/" + MYGENE_ID).json()
        assert res.get('info', {}).get('title', '') == "MyGene.info API"

        res = self.request("/api/metadata/" + MYCHEM_ID).json()
        assert res.get('info', {}).get('title', '') == "MyChem.info API"

        res = self.request("/api/metadata/" + MYGENE_ID + "?format=yaml")
        yaml.load(res.text, Loader=yaml.SafeLoader)

    def test_get_all(self):
        '''
        [READ] Get all
        '''
        res = self.request("/api/metadata/", method='GET').json()
        assert len(res) == 2

        res = self.request("/api/metadata?from_=1", method='GET').json()
        assert len(res) == 1

        res = self.request("/api/metadata?size=1", method='GET').json()
        assert len(res) == 1

    def test_post(self):

        _ID = '1ad2cba40cb25cd70d00aa8fba9cfaf3'
        VALID_V3_URL = \
            'https://raw.githubusercontent.com/schurerlab/'\
            'smartAPIs/master/LINCS_Data_Portal_smartAPIs.yml'

        try:
            smartapi = SmartAPI.get(_ID)
            smartapi.delete()
            refresh()
        except NotFoundError:
            pass

        self.request("/api/metadata/", method='POST', data={'url': VALID_V3_URL}, expect=401)
        self.request("/api/metadata/", method='POST', data={'url': MYGENE_URL}, headers=self.auth_user, expect=409)
        self.request("/api/metadata/", method='POST', headers=self.auth_user, expect=400)
        self.request("/api/metadata/", method='POST', data={'url': "http://invalidhost/file"}, headers=self.auth_user, expect=400)
        self.request("/api/metadata/", method='POST', data={'url': VALID_V3_URL, 'dryrun': True}, headers=self.auth_user)
        refresh()
        assert not SmartAPI.exists(_ID)
        self.request("/api/metadata/", method='POST', data={'url': VALID_V3_URL}, headers=self.auth_user)
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

        self.request("/api/metadata/" + MYGENE_ID, method='PUT', data={"slug": "mygeeni"}, expect=401)
        self.request("/api/metadata/" + MYGENE_ID, method='PUT', data={"slug": "mygeeni"}, headers=self.evil_user, expect=403)
        self.request("/api/metadata/" + MYGENE_ID, method='PUT', data={"slug": "my"}, headers=self.auth_user, expect=400)
        self.request("/api/metadata/" + MYGENE_ID, method='PUT', data={"slug": "www"}, headers=self.auth_user, expect=400)
        self.request("/api/metadata/" + MYGENE_ID, method='PUT', data={"slug": "MYGENE"}, headers=self.auth_user, expect=400)
        self.request("/api/metadata/" + MYGENE_ID, method='PUT', data={"slug": "mygene!!"}, headers=self.auth_user, expect=400)
        self.request("/api/metadata/" + MYGENE_ID, method='PUT', data={"slug": "mygeeni"}, headers=self.auth_user)

        refresh()
        assert not SmartAPI.find("mygene")
        assert SmartAPI.find("mygeeni")

        self.request("/api/metadata/" + MYGENE_ID, method='PUT', data={"slug": ""}, headers=self.auth_user)

        refresh()
        assert not SmartAPI.find("mygeeni")
        assert not SmartAPI.find("mygene")

        self.request("/api/metadata/" + MYGENE_ID, method='PUT', data={"slug": "mygene"}, headers=self.auth_user)
        refresh()
        assert not SmartAPI.find("mygeeni")
        assert SmartAPI.find("mygene")

        # teardown
        refresh()
        if not SmartAPI.find("mygene"):
            mygene = APIDoc(meta={'id': MYGENE_ID}, **MYGENE_ES)
            mygene._raw = decoder.compress(MYGENE_RAW)
            mygene.save()

    def test_update_doc(self):
        pass  # TODO

    def test_delete(self):

        # setup
        assert SmartAPI.exists(MYGENE_ID)

        self.request("/api/metadata/" + MYGENE_ID, method='DELETE', expect=401)
        self.request("/api/metadata/" + MYGENE_ID, method='DELETE', headers=self.evil_user, expect=403)
        self.request("/api/metadata/" + MYGENE_ID, method='DELETE', headers=self.auth_user)

        refresh()
        assert not SmartAPI.exists(MYGENE_ID)

        # teardown
        refresh()
        if not SmartAPI.exists(MYGENE_ID):  # recover the deleted file
            mygene = APIDoc(meta={'id': MYGENE_ID}, **MYGENE_ES)
            mygene._raw = decoder.compress(MYGENE_RAW)
            mygene.save()
        refresh()
