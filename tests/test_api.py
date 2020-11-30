
import pytest
import random
from datetime import datetime as dt
import sys
sys.path.append("..")

from src.web.api.model.api_doc import API_Doc
from src.web.api.controllers.controller import APIDocController

from src.web.api.controllers.controller import APIMetadata
from src.web.api.controllers.controller import get_api_metadata_by_url



class TestAPIMetadata:

    _doc_id = ''

    _test_slug = 'test_slug_'+str(random.randint(1, 21))

    _user = {"login": "marcodarko"}

    # *****************************************************************************
    # SETUP
    # *****************************************************************************

    @classmethod
    def setup_class(self):
        """ setup any state specific to the execution of the given tests.
        """
        url = 'https://raw.githubusercontent.com/marcodarko/api_exmaple/master/api.yml'

        data = get_api_metadata_by_url(url)
        data = data.get('metadata', None)
        data['_meta'] = {"github_username": self._user['login'], 'url': url, 'timestamp': dt.now().isoformat()}

        metadata = APIMetadata(data)
        
        api_id = metadata.encode_api_id()
        self._doc_id = api_id
        doc = API_Doc(meta={'id': api_id}, ** metadata.convert_es())
        doc.save()

    # *****************************************************************************
    # CONTROLLER TESTS
    # *****************************************************************************

    def test_controller_get_all(self):
        """
        Get ALL docs
        """
        doc = APIDocController.get_api(api_name='all')
        assert isinstance(doc, dict)

    def test_controller_get_one(self):
        """
        Get ALL docs
        """
        name = 'MARCO API'

        doc = APIDocController.get_api(api_name=name)
        assert isinstance(doc, dict)

    def test_controller_get_tags(self):
        """
        Get tag aggregations for field
        """
        field = 'info.contact.name'
        size = 100

        res = APIDocController.get_tags(field=field, size=size)
        assert len(res.get('aggregations', {}).get('field_values', {}).get('buckets', [])) >= 1 

    def test_controller_update_slug(self):
        """
        Update registered slug name for ID
        """
        api_id = self._doc_id 
        slug = self._test_slug
        user = self._user

        doc = APIDocController(api_id)
        res = doc.update(_id=api_id, user=user, slug_name=slug)
        assert res.get(f'{api_id}._meta.slug', False) == slug

    # *****************************************************************************
    # MODEL TESTS
    # *****************************************************************************

    def test_model_doc_exists(self):
        """
        Existing ID exists
        """
        exists = API_Doc.exists(_id=self._doc_id)
        assert exists

    def test_model_doc_doesnt_exist(self):
        """
        Fake ID does not exists
        """
        exists = API_Doc.exists(_id='id123779328749279')
        assert not exists

    def test_model_slug_taken(self):
        """
        Slug name already exists
        """
        slug_exists = API_Doc.slug_exists(slug=self._test_slug)
        assert slug_exists == True

    def test_model_slug_available(self):
        """
        Slug name is available
        """
        slug_exists = API_Doc.slug_exists(slug='new_slug')
        assert slug_exists == False

    def test_model_tag_aggregation(self):
        """
        Confirm aggregations exists for field, eg. tags
        """
        field = 'info.contact.name'
        agg_name = 'field_values'

        res = API_Doc.aggregate(field=field, size=100, agg_name=agg_name).to_dict()
        assert len(res.get('aggregations', {}).get(agg_name, {}).get('buckets', [])) >= 1 
    
    # def test_delete_doc(self):
    #     """
    #     delete doc
    #     """
    #     doc = API_Doc()
    #     doc = doc.get(id=self._doc_id)
    #     res = doc.delete(id=self._doc_id)
    #     assert res == True

    # *****************************************************************************
    # TEARDOWN
    # *****************************************************************************
    @classmethod
    def teardown_class(self):
        """ teardown any state that was previously setup.
        """
        print("teardown")