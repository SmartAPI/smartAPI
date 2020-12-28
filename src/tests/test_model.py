import pytest

from web.api.model import API_Doc


def test_doc_exists():
    """
    Existing ID exists
    """
    _id = 'f307760715d91908d0ae6de7f0810b22'
    exists = API_Doc.exists(_id=_id)

def test_doc_doesnt_exist():
    """
    Fake ID does not exists
    """
    exists = API_Doc.exists(_id='id123779328749279')
    assert not exists

def test_slug_available():
    """
    Slug name is available
    """
    slug_exists = API_Doc.slug_exists(slug='new_slug')
    assert slug_exists is False

def test_tag_aggregation():
    """
    Confirm aggregations exists for field, eg. tags
    """
    field = 'info.contact.name'
    agg_name = 'field_values'

    res = API_Doc.aggregate(field=field, size=100, agg_name=agg_name).to_dict()
    assert len(res.get('aggregations', {}).get(agg_name, {}).get('buckets', [])) >= 1

# def test_delete_doc():
#     """
#     delete doc
#     """
#     _id = '3912601003e25befedfb480a5687ab07'
#     doc = API_Doc()
#     doc = doc.get(id=_id)
#     res = doc.delete(id=s_id)
#     assert res.get('success') == True
