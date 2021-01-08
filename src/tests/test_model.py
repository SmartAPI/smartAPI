import pytest

from model import APIDoc

doc_1_id = '59dce17363dce279d389100834e43648'

test_doc = {
    "openapi": "3.0.0",
    "info": {
        "version": "1.0.0",
        "title": "AEOLUsrs API",
        "description": "Documentation of the A curated and standardized adverse drug event resource to accelerate drug safety research (AEOLUS) web query services. Learn more about the underlying dataset [HERE](https://www.nature.com/articles/sdata201626)",
        "termsOfService": "http://tsing.cm/terms/",
        "contact": {
            "name": "Juan M. Banda",
            "x-role": "responsible developer",
            "email": "jmbanda@stanford.edu",
            "x-id": "http://orcid.org/0000-0001-8499-824X"
        },
        "x-maturity": "development",
        "x-implementationLanguage": "PHP"
    },
    "externalDocs": {
        "description": "Find more info here",
        "url": "http://ec2-54-186-230-27.us-west-2.compute.amazonaws.com:8080/swagger-ui.html"
    },
    "_meta": {
        "github_username": "marcodarko",
        "url": "https://raw.githubusercontent.com/jmbanda/biohack2017_smartAPI/master/AEOLUSsrsAPI-v1.0.json",
        "timestamp": "2020-12-30T12:06:42.771619+00:00",
        "ETag": "57282573850cdaf330d5f44d91c899c70ca4b39292c3fc446574b99abc069510"
    },
}

@pytest.fixture(autouse=True, scope='module')
def setup_fixture():
    """
    Get data from test urls
    """
    if APIDoc.exists(doc_1_id):
        doc = APIDoc()
        doc = doc.get(doc_1_id)
        doc.delete()
    new_doc = APIDoc(meta={'id': doc_1_id}, **test_doc)
    new_doc.save()

def test_doc_exists():
    """
    Existing ID exists
    """
    assert APIDoc.exists(doc_1_id)

def test_doc_does_not_exist():
    """
    Fake ID does not exists
    """
    assert not APIDoc.exists(_id='id123779328749279')

def test_slug_available():
    """
    Slug name is available
    """
    slug_exists = APIDoc.slug_exists(slug='new_slug')
    assert slug_exists is False

def test_tag_aggregation():
    """
    Confirm aggregations exists for field, eg. tags
    """
    field = 'info.contact.name'
    agg_name = 'field_values'

    res = APIDoc.aggregate(field=field, size=100, agg_name=agg_name).to_dict()
    assert len(res.get('aggregations', {}).get(agg_name, {}).get('buckets', [])) >= 1

def test_delete_doc():
    """
    delete doc
    """
    doc = APIDoc()
    doc = doc.get(doc_1_id)
    doc.delete()
    assert not APIDoc.exists(_id=doc_1_id)
