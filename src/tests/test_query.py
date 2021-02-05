'''
    Biothings ESQueryHandler Type Tester
'''
import os

import pytest
from biothings.tests.web import BiothingsTestCase
from tornado.escape import json_encode
from tornado.web import create_signed_value
from controller import SmartAPI
from utils.indices import refresh

dirname = os.path.dirname(__file__)

MYGENE_URL = 'https://raw.githubusercontent.com/NCATS-Tangerine/'\
    'translator-api-registry/master/mygene.info/openapi_full.yml'
MYCHEM_URL = 'https://raw.githubusercontent.com/NCATS-Tangerine/'\
    'translator-api-registry/master/mychem.info/openapi_full.yml'

MYGENE_ID = '59dce17363dce279d389100834e43648'
MYCHEM_ID = '8f08d1446e0bb9c2b323713ce83e2bd3'


# prepare data to be saved in tests
with open(os.path.join(dirname, 'mygene.yml'), 'rb') as file:
    MYGENE_DATA = file.read()

with open(os.path.join(dirname, 'mychem.yml'), 'rb') as file:
    MYCHEM_DATA = file.read()

@pytest.fixture(scope="module", autouse=True)
def setup():
    """
    setup state called once for the class
    """
    if not SmartAPI.exists(MYGENE_ID):
        doc = SmartAPI(MYGENE_URL, MYGENE_DATA)
        doc.username = 'marcodarko'
        doc.save()
        refresh()
    if not SmartAPI.exists(MYCHEM_ID):
        doc = SmartAPI(MYCHEM_URL, MYCHEM_DATA)
        doc.username = 'marcodarko'
        doc.save()
        refresh()


class SmartAPIQueryTest(BiothingsTestCase):

    @classmethod
    def cookie_header(cls, username):
        cookie_name, cookie_value = 'user', {'github_username': username}
        secure_cookie = create_signed_value(
            cls.settings.COOKIE_SECRET, cookie_name,
            json_encode(cookie_value))
        return {'Cookie': '='.join((cookie_name, secure_cookie.decode()))}

    @property
    def auth_user(self):
        return self.cookie_header('marcodarko')

    @property
    def evil_user(self):
        return self.cookie_header('eviluser01')


    def test_100_all(self):
        '''
        [QUERY] Basic functionality
        '''
        res = self.query(q='__all__')
        assert bool(res['total'])

    def test_101_query(self):
        '''
        [QUERY] Customization by properties
        '''
        self.query(q='mygene')

    def test_102_named_field(self):
        ''' Query named field '''
        self.query(q='tags.name:translator')

    def test_103_match_all(self):
        ''' Query all documents '''
        self.query(q='__all__')

    def test_105_filters(self):
        ''' Query with multiple any fields in json format '''
        flt = '{"tags.name.raw":["chemical"], "info.contact.name.raw":["Chunlei Wu"]}'
        res = self.query(q='__all__', filters=flt)
        assert res['hits'][0]['info']['title'] == "MyChem.info API"
        assert len(res['hits']) == 1

    def test_106_filters(self):
        ''' tag filter '''
        res = self.query(q='__all__', tags='"chemical", "drug"')
        assert res['hits'][0]['info']['title'] == "MyChem.info API"
        assert len(res['hits']) == 1

    def test_107_filters(self):
        ''' authors filter '''
        res = self.query(q='__all__', authors='"Chunlei Wu"')
        assert len(res['hits']) == 2

def teardown_module():
    """
    teardown any state that was previously setup.
    called once for the class
    """
    for _id in [MYGENE_ID, MYCHEM_ID]:
        if SmartAPI.exists(_id):
            doc = SmartAPI.get(_id)
            doc.delete()
