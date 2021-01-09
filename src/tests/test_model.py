import pytest

from model import APIDoc

MYDISEASE_ID = 'f307760715d91908d0ae6de7f0810b22'

MYDISEASE_DATA = {
    "openapi": "3.0.0",
    "info": {
        "version": "1.0",
        "title": "MyDisease.info API",
        "description": "Documentation of the MyDisease.info disease query web services.  Learn more about [MyDisease.info](http://MyDisease.info/)",
        "termsOfService": "http://MyDisease.info/terms",
        "contact": {
            "name": "Chunlei Wu",
            "x-role": "responsible developer",
            "email": "help@biothings.io",
            "x-id": "https://github.com/newgene"
        }
    },
    "servers": [
        {
            "url": "http://MyDisease.info/v1",
            "description": "Production server"
        }
    ],
    "tags": [
        {
            "name": "disease"
        },
        {
            "name": "query"
        },
        {
            "name": "metadata"
        }
    ],
    "paths": {
        "/metadata/fields": {
            "get": {
                "tags": [
                    "metadata"
                ],
                "summary": "Get metadata about the data fields available from a MyDisease.info disease object",
                "parameters": [
                    {
                        "name": "search",
                        "$ref": "#/components/parameters/search"
                    }
                ],
                "responses": {
                    "200": {
                        "description": "MyDisease.info metadata fields object"
                    }
                }
            }
        }
    },
    "components": {
        "parameters": {
            "search": {
                "name": "search",
                "in": "query",
                "description": "Pass a search term to filter the available fields. Type: string. Default: None.",
                "schema": {
                    "type": "string"
                }
            }
        },
        "schemas": {
            "string_or_array": {
                "oneOf": [
                    {
                        "items": {
                            "type": "string"
                        },
                        "type": "array"
                    },
                    {
                        "type": "string"
                    }
                ]
            }
        }
    }
}

@pytest.fixture(autouse=True, scope='module')
def setup_fixture():
    """
    Get data from test urls
    """
    if APIDoc.exists(MYDISEASE_ID):
        doc = APIDoc.get(MYDISEASE_ID)
        doc.delete()
    new_doc = APIDoc(meta={'id': MYDISEASE_ID}, **MYDISEASE_DATA)
    new_doc.save()

def test_doc_exists():
    """
    Existing ID exists
    """
    assert APIDoc.exists(MYDISEASE_ID)

def test_doc_does_not_exist():
    """
    Fake ID does not exists
    """
    assert not APIDoc.exists('id123779328749279')

def test_slug_available():
    """
    Slug name is available
    """
    assert not APIDoc.slug_exists(slug='new_slug')

def test_tag_aggregation():
    """
    Confirm aggregations exists for field, eg. tags
    """
    res = APIDoc.aggregate(field='info.contact.name', size=100, agg_name='field_values').to_dict()
    assert len(res.get('aggregations', {}).get('field_values', {}).get('buckets', [])) >= 1

def test_delete_doc():
    """
    delete doc
    """
    doc = APIDoc.get(MYDISEASE_ID)
    doc.delete()
    assert not APIDoc.exists(MYDISEASE_ID)
