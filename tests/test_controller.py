
import pytest
import random

from src.web.api.model import API_Doc
from src.web.api.controllers.controller import APIDocController

from src.web.api.controllers.controller import SlugRegistrationError


class TestController:

    _doc_id = '3912601003e25befedfb480a5687ab07'

    _test_slug = 'test_slug_'+str(random.randint(1, 21))

    _user = {"login": "marcodarko"}

    test_doc = {
        "openapi": "3.0.0",
        "info": {
            "contact": {
                "email": "help@mygene.info",
                "name": "Marco Cano",
                "x-id": "https://github.com/newgene",
                "x-role": "responsible developer"
            },
            "description": "Documentation of the MyGene.info Gene Query web services. Learn more about [MyGene.info](http://mygene.info/)",
            "termsOfService": "http://mygene.info/terms/",
            "title": "TEST API",
            "version": "3.0"
        },
        "servers": [
            {
                "description": "Encrypted Production server",
                "url": "https://mygene.info/v3"
            },
            {
                "description": "Production server",
                "url": "http://mygene.info/v3"
            }
        ],
        "tags": [
            {
                "name": "gene"
            },
            {
                "name": "annotation"
            },
            {
                "name": "query"
            },
            {
                "name": "translator"
            },
            {
                "name": "biothings"
            }
        ],
        "paths": [
            {
                "path": "/metadata",
                "pathitem": {
                    "get": {
                        "parameters": [
                            {
                                "$ref": "#/components/parameters/callback",
                                "name": "callback"
                            }
                        ],
                        "responses": {
                            "200": {
                                "description": "MyGene.info metadata object"
                            }
                        },
                        "summary": "Get metadata about the data available from MyGene.info."
                    }
                }
            },
        ],
        "components": {
            "parameters": {},
            "schemas": {},
            "x-bte-kgs-operations": {},
            "x-bte-response-mapping": {}
        },
        "_meta": {
            "github_username": "marcodarko",
            "url": "https://raw.githubusercontent.com/marcodarko/api_exmaple/master/api.yml",
            "timestamp": "2020-12-01T15:17:45.862906+00:00",
            "ETag": "d178b8f1976d3aadd8bed151614445e5fc17cc9548e174dcebbc42a60eb086cf"
        },
    }

    # *****************************************************************************
    # SETUP
    # *****************************************************************************

    @classmethod
    def setup_class(cls):
        """ 
        Model is given an already transformed doc with an already encoded ID 
        and _meta field with test user
        """
        doc = API_Doc(meta={'id': cls._doc_id}, ** cls.test_doc)
        doc.save()

    # *****************************************************************************
    # CONTROLLER TESTS
    # *****************************************************************************

    def test_get_all(self):
        """
        Get ALL docs, since one doc expect dict not list
        """
        docs = APIDocController.get_api(api_name='all')
        assert isinstance(docs, dict)

    def test__get_api(self):
        """
        Get one doc by ID
        """
        _id = self._doc_id

        doc = APIDocController.get_api(api_name=_id)
        assert isinstance(doc, dict)

    def test__get_tags(self):
        """
        Get tag aggregations for field
        """
        field = 'info.contact.name'
        size = 100

        res = APIDocController.get_tags(field=field, size=size)
        assert len(res.get('aggregations', {}).get('field_values', {}).get('buckets', [])) >= 1 

    def test_validate_slug(self):
        """
        Update registered slug name for ID
        """
        api_id = self._doc_id
        slug = self._test_slug

        doc = APIDocController(api_id)
        valid = doc._validate_slug_name(slug_name=slug)
        assert valid is True

    def test_validate_slug_invalid(self):
        """
        Update registered slug name for ID
        """
        api_id = self._doc_id
        invalid_slug = 'smart-api'

        failed = False
        try:
            doc = APIDocController(api_id)
            doc._validate_slug_name(slug_name=invalid_slug)
        except SlugRegistrationError:
            failed = True
        assert failed

    def test_update_slug(self):
        """
        Update registered slug name for ID
        """
        api_id = self._doc_id
        slug = self._test_slug
        user = self._user

        doc = APIDocController(api_id)
        res = doc.update(_id=api_id, user=user, slug_name=slug)
        assert res.get(f'{api_id}._meta.slug', False) == slug

    # model has to test is taken first
    def test_model_slug_taken(self):
        """
        Slug name already exists
        """
        slug_exists = API_Doc.slug_exists(slug=self._test_slug)
        assert slug_exists is True

    def test_delete_slug(self):
        """
        Delete slug for ID
        """
        api_id = self._doc_id
        slug = self._test_slug
        user = self._user

        doc = APIDocController(api_id)
        res = doc.delete_slug(_id=api_id, user=user, slug_name=slug)
        assert res == f"slug '{slug}' for {api_id} was deleted"

    def test_refresh_api(self):
        """
        Refresh single api with id
        """
        api_id = self._doc_id
        user = self._user

        doc = APIDocController(api_id)
        res = doc.refresh_api(_id=api_id, user=user, test=True)
        assert res.get('test-updated', '') == f"API with ID {api_id} was refreshed"

    # *****************************************************************************
    # TEARDOWN
    # *****************************************************************************
    @classmethod
    def teardown_class(cls):
        """ teardown any state that was previously setup.
        """
        print("teardown")
        # make sure its deleted 