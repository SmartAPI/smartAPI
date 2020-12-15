import os

import json
import pytest

from web.api.model import API_Doc
from web.api.controller import APIDocController, SlugRegistrationError

class TestController:

    _doc_id = 'f307760715d91908d0ae6de7f0810b22'

    _doc_id_two = '59dce17363dce279d389100834e43648'

    _test_slug = 'myslug'

    _user = {"login": "marcodarko"}

    @classmethod
    def setup_class(cls):
        """ 
        Model is given an already transformed doc with an already encoded ID 
        and _meta field with test user
        """
        with open(os.path.join(os.path.dirname(__file__), "data/mygene.json")) as f:
            my_gene = json.load(f)
            print(my_gene)

        with open(os.path.join(os.path.dirname(__file__), "data/mydisease.json")) as f:
            my_disease = json.load(f)
            print(my_disease)

        doc = API_Doc(meta={'id': cls._doc_id}, ** my_disease)
        doc.save()

        doc = API_Doc(meta={'id': cls._doc_id_two}, ** my_gene)
        doc.save()

    # *****************************************************************************
    # CONTROLLER TESTS
    # *****************************************************************************

    def test_get_all(self):
        """
        Get ALL docs
        """
        docs = APIDocController.get_all()
        assert isinstance(docs, list)

    def test_get_one(self):
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
        slug = self._test_slug
        APIDocController.validate_slug_name(slug_name=slug)
        assert True

    def test_validate_slug_invalid(self):
        """
        Update registered slug name for ID
        """
        invalid_slug = 'smart-api'
        try:
            APIDocController.validate_slug_name(slug_name=invalid_slug)
        except SlugRegistrationError:
            pass
        else:
            assert False

    def test_update_slug(self):
        """
        Update registered slug name for ID
        """
        api_id = self._doc_id
        slug = self._test_slug
        user = self._user

        doc = APIDocController(api_id)
        res = doc.update_slug(_id=api_id, user=user, slug_name=slug)
        assert res.get(f'{api_id}._meta.slug', False) == slug

    def test__get_api_from_slug(self):
        """
        Get ID of doc with slug
        """
        slug = self._test_slug

        _id = APIDocController.get_api_id_from_slug(slug=slug)
        assert isinstance(_id, str)

    def test_model_slug_taken(self):
        """
        Slug name already exists
        """
        APIDocController.slug_is_available(slug=self._test_slug)

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

    @classmethod
    def teardown_class(cls):
        """ teardown any state that was previously setup.
        """
        print("teardown")
        # TODO make sure its deleted 