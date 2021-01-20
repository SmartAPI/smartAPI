'''
    Biothings ESQueryHandler Type Tester
'''
import json
import os

import pytest
import yaml
from biothings.tests.web import BiothingsTestCase
from tornado.escape import json_encode
from tornado.web import create_signed_value
from controller import SmartAPI
from utils.indices import refresh

VALID_V3_URL = 'https://raw.githubusercontent.com/schurerlab/'\
    'smartAPIs/master/LINCS_Data_Portal_smartAPIs.yml'

API_ID = '1ad2cba40cb25cd70d00aa8fba9cfaf3'

INVALID_V3_URL = 'https://raw.githubusercontent.com/marcodarko/api_exmaple/master/api.yml'

MYGENE_URL = 'https://raw.githubusercontent.com/NCATS-Tangerine/'\
    'translator-api-registry/master/mygene.info/openapi_full.yml'

MYGENE_ID = '59dce17363dce279d389100834e43648'

USER = {"github_username": "marcodarko"}

dirname = os.path.dirname(__file__)

# prepare data to be saved in tests
with open(os.path.join(dirname, 'mygene.json'), 'r') as file:
    MYGENE_DATA = json.load(file)

@pytest.fixture(scope="module", autouse=True)
def setup():
    """
    setup state called once for the class
    """
    for _id in [MYGENE_ID, API_ID]:
        if SmartAPI.exists(_id):
            doc = SmartAPI.get_api_by_id(_id)
            doc.delete()

class SmartAPITest(BiothingsTestCase):
    '''
    SmartAPI metadata instance controller tests
    '''

    @classmethod
    def cookie_header(cls, username):
        '''
        request header
        '''
        cookie_name, cookie_value = 'user', {'login': username}
        secure_cookie = create_signed_value(
            cls.settings.COOKIE_SECRET, cookie_name,
            json_encode(cookie_value))
        return {'Cookie': '='.join((cookie_name, secure_cookie.decode()))}

    @property
    def auth_user(self):
        '''
        authorized user
        '''
        return self.cookie_header('marcodarko')

    @property
    def evil_user(self):
        '''
        unauthorized user
        '''
        return self.cookie_header('eviluser01')

    # ****** VALIDATOR *******
    def test_001_validate_valid_url(self):
        '''
        [POST] with url
        '''
        self.request(
            "/api/validate/",
            method='POST',
            data={'url': VALID_V3_URL})

    def test_002_validate_invalid_url(self):
        '''
        [POST] with url invalid data
        '''
        self.request(
            "/api/validate/",
            method='POST',
            data={'url': INVALID_V3_URL},
            expect=400)

    def test_003_validate_body_json(self):
        '''
        [POST] with body JSON
        '''
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        self.request(
            "/api/validate/",
            method='POST',
            json=MYGENE_DATA,
            headers=headers,
            expect=200)

    def test_004_validate_body_yaml(self):
        '''
        [POST] with body YAML
        '''
        yaml_doc = """
            openapi: '3.0.0'
            info:
            version: 1.0.0
            title: AEOLUsrs API
            description: >-
                Documentation of the A curated and standardized adverse drug event resource
                to accelerate drug safety research (AEOLUS) web query services. Learn more
                about the underlying dataset [HERE](https://www.nature.com/articles/sdata201626)
            termsOfService: 'http://tsing.cm/terms/'
            contact:
                name: Juan M. Banda
                x-role: responsible developer
                email: jmbanda@stanford.edu
                x-id: 'http://orcid.org/0000-0001-8499-824X'
            x-maturity: development
            x-implementationLanguage: PHP
            externalDocs:
            description: Find more info here
            url: 'http://ec2-54-186-230-27.us-west-2.compute.amazonaws.com:8080/swagger-ui.html'
            x-externalResources:
            - x-url: 'http://ec2-54-186-230-27.us-west-2.compute.amazonaws.com:8080/swagger-ui.html'
                x-type: api documentation
            - x-url: 'https://doi.org/10.1038/sdata.2016.26'
                x-type: publication
                x-description: 'A curated and standardized adverse drug event resource to accelerate drug safety research'
            - x-url: 'https://twitter.com/drjmbanda'
                x-type: social media
            servers:
            - url: 'http://ec2-54-186-230-27.us-west-2.compute.amazonaws.com:8080/v3'
                description: Development server
                x-location: 'California, USA'
                variables:
                port: {
                    "enum": ['8080'],
                    "default": '8080'
                    }
            tags:
            - x-id: 'http://purl.bioontology.org/ontology/MESH/D016907'
                name: Adverse Drug Reaction Reporting Systems
            """

        headers = {'Content-type': 'application/yaml', 'Accept': 'text/plain'}
        self.request(
            "/api/validate/",
            method='POST',
            json=MYGENE_DATA,
            headers=headers,
            expect=200)

    # ****** METADATA *******

    def test_101_not_authorized(self):
        '''
        [CREATE] Unauthorized
        '''
        self.request(
            "/api/metadata/",
            method='POST',
            data={'url': VALID_V3_URL},
            expect=401)

    def test_102_dryrun(self):
        '''
        [CREATE] save doc
        '''
        body = {
            'url': VALID_V3_URL,
            'dryrun': True
        }
        res = self.request(
            "/api/metadata/",
            method='POST',
            data=body,
            headers=self.auth_user).json()
        assert res.get('success')
        assert res.get('details') == '[Dryrun] Valid v3 Metadata'

    def test_103_create(self):
        '''
        [CREATE] save doc
        '''
        res = self.request(
            "/api/metadata/",
            method='POST',
            data={'url': VALID_V3_URL},
            headers=self.auth_user).json()
        refresh()
        assert res.get('success', False)
        assert SmartAPI.exists(API_ID)

    def test_104_refuse_overwrite(self):
        '''
        [CREATE] Disallow overwriting of docs not owned
        '''
        refresh()
        if not SmartAPI.exists(MYGENE_ID):
            doc = SmartAPI.from_dict(MYGENE_DATA)
            doc.url = MYGENE_URL
            doc.username = 'marcodarko'
            doc.save()
            refresh()
        body = {
            'url': MYGENE_URL,
            'overwrite': True
        }
        self.request(
            "/api/metadata/",
            method='POST',
            data=body,
            headers=self.evil_user,
            expect=401)

    def test_105_allow_overwrite(self):
        '''
        [CREATE] Allow overwriting of doc
        '''
        body = {
            'url': VALID_V3_URL,
            'overwrite': True
        }
        res = self.request(
            "/api/metadata/",
            method='POST',
            data=body,
            headers=self.auth_user).json()
        assert res.get('success')


    def test_106_get_one(self):
        '''
        [READ] Get one doc by id
        '''
        refresh()
        if not SmartAPI.exists(MYGENE_ID):
            doc = SmartAPI.from_dict(MYGENE_DATA)
            doc.url = MYGENE_URL
            doc.username = 'marcodarko'
            doc.save()
            refresh()

        res = self.request(
            "/api/metadata/"+MYGENE_ID,
            method='GET').json()
        assert res.get('info', {}).get('title', '') == "MyGene.info API"

    def test_107_get_one_format(self):
        '''
        [READ] Get one with format
        '''
        refresh()
        if not SmartAPI.exists(MYGENE_ID):
            doc = SmartAPI.from_dict(MYGENE_DATA)
            doc.url = MYGENE_URL
            doc.username = 'marcodarko'
            doc.etag = 'I'
            doc.save()
            refresh()

        res = self.request(
            "/api/metadata/"+MYGENE_ID+"?format=yaml",
            method='GET')
        yaml.load(res.text, Loader=yaml.SafeLoader)

    def test_108_get_all(self):
        '''
        [READ] Get all
        '''
        res = self.request("/api/metadata/", method='GET').json()
        assert len(res)

    def test_109_get_all_with_fields(self):
        '''
        [READ] Get all docs with specific fields
        '''
        refresh()
        if not SmartAPI.exists(MYGENE_ID):
            doc = SmartAPI.from_dict(MYGENE_DATA)
            doc.url = MYGENE_URL
            doc.username = 'marcodarko'
            doc.save()
            refresh()

        res = self.request("/api/metadata?fields=info,_meta", method='GET').json()
        assert res[0].get('info', {}).get('title', '') == 'MyGene.info API'
        assert res[0].get('_meta', {}).get('github_username', '') == 'marcodarko'
        assert not res[0].get('paths', {})

    def test_110_get_all_from(self):
        '''
        [READ] Get all docs from
        '''
        res = self.request("/api/metadata?_from=1", method='GET').json()
        assert len(res) == 1

    def test_111_get_all_size(self):
        '''
        [READ] Get specific size response
        '''
        refresh()
        if not SmartAPI.exists(MYGENE_ID):
            doc = SmartAPI.from_dict(MYGENE_DATA)
            doc.url = MYGENE_URL
            doc.username = 'marcodarko'
            doc.save()
            refresh()

        res = self.request("/api/metadata?size=1", method='GET').json()
        assert len(res) == 1

    def test_112_update_not_allowed(self):
        '''
        [UPDATE] Unauthorized
        '''
        refresh()
        if not SmartAPI.exists(MYGENE_ID):
            doc = SmartAPI.from_dict(MYGENE_DATA)
            doc.url = MYGENE_URL
            doc.username = 'marcodarko'
            doc.save()
            refresh()

        body = {
            'slug': 'lincs_slug'
        }
        self.request(
            "/api/metadata/"+MYGENE_ID,
            method='PUT',
            data=body,
            headers=self.evil_user,
            expect=401)

    def test_113_update(self):
        '''
        [UPDATE]
        '''
        refresh()
        if not SmartAPI.exists(MYGENE_ID):
            doc = SmartAPI.from_dict(MYGENE_DATA)
            doc.url = MYGENE_URL
            doc.username = 'marcodarko'
            doc.save()
            refresh()

        body = {
            'slug': 'lincs_slug'
        }
        res = self.request(
            "/api/metadata/"+MYGENE_ID,
            method='PUT',
            data=body,
            headers=self.auth_user).json()
        assert res.get('success', False)
        assert res.get('details', '') == MYGENE_ID

    def test_114_update_refresh(self):
        '''
        [UPDATE] refresh doc by registered url
        '''
        refresh()
        if not SmartAPI.exists(MYGENE_ID):
            doc = SmartAPI.from_dict(MYGENE_DATA)
            doc.url = MYGENE_URL
            doc.username = 'marcodarko'
            doc.save()
            refresh()

        res = self.request(
            "/api/metadata/"+MYGENE_ID,
            method='PUT',
            headers=self.auth_user).json()
        assert res.get('success', False)

    def test_115_delete_not_allowed(self):
        '''
        [DELETE] Unauthorized
        '''
        refresh()
        if not SmartAPI.exists(MYGENE_ID):
            doc = SmartAPI.from_dict(MYGENE_DATA)
            doc.url = MYGENE_URL
            doc.username = 'marcodarko'
            doc.save()
            refresh()

        self.request(
            "/api/metadata/"+MYGENE_ID,
            method='DELETE',
            headers=self.evil_user,
            expect=401)

    def test_116_delete(self):
        '''
        [DELETE]
        '''
        refresh()
        if not SmartAPI.exists(MYGENE_ID):
            doc = SmartAPI.from_dict(MYGENE_DATA)
            doc.url = MYGENE_URL
            doc.username = 'marcodarko'
            doc.save()
            refresh()

        res = self.request(
            "/api/metadata/"+MYGENE_ID,
            method='DELETE',
            headers=self.auth_user).json()
        assert res.get('success')

    # ****** SUGGESTION *******

    def test_201_suggestion(self):
        '''
        [GET] get aggregations for field
        '''
        refresh()
        if not SmartAPI.exists(MYGENE_URL, '_meta.url'):
            doc = SmartAPI.from_dict(MYGENE_DATA)
            doc.url = MYGENE_URL
            doc.username = 'marcodarko'
            doc.save()
            refresh()

        res = self.request(
            "/api/suggestion?field=tags.name",
            method='GET',
            headers=self.auth_user).json()
        assert len(res.get('aggregations', {}).get('field_values', {}).get('buckets', [])) >= 1


def teardown_module():
    """
    teardown any state that was previously setup.
    called once for the class
    """
    for _id in [MYGENE_ID, API_ID]:
        if SmartAPI.exists(_id):
            doc = SmartAPI.get_api_by_id(_id)
            doc.delete()
