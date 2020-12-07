import pytest

from web.api.model import API_Doc
    
class TestDocModel:

    _doc_id = '3912601003e25befedfb480a5687ab07' 
    # *****************************************************************************
    # MODEL TESTS
    # *****************************************************************************

    def test_doc_exists(self):
        """
        Existing ID exists
        """
        exists = API_Doc.exists(_id=self._doc_id)
        assert exists

    def test_doc_doesnt_exist(self):
        """
        Fake ID does not exists
        """
        exists = API_Doc.exists(_id='id123779328749279')
        assert not exists

    def test_slug_available(self):
        """
        Slug name is available
        """
        slug_exists = API_Doc.slug_exists(slug='new_slug')
        assert slug_exists is False

    def test_tag_aggregation(self):
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
    #     assert res.get('success') == True
