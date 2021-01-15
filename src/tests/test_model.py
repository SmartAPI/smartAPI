import pytest

from model import APIDoc
from utils.indices import refresh

MYDISEASE_ID = 'f307760715d91908d0ae6de7f0810b22'

MYDISEASE_DATA = {
    "_meta": {
        "ETag": "659023576fb3c74c5a6eb4ec3987fba0d4164f060ab33c5040c0386ac18544b2",
        "github_username": "cyrus0824",
        "slug": "mydisease",
        "timestamp": "2019-10-22T04:26:58.530282",
        "url": "https://raw.githubusercontent.com/biothings/mydisease.info/master/mydisease/swagger/mydisease.yml"
    },
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

def test_save():
    """
    Save doc
    """
    new_doc = APIDoc(**MYDISEASE_DATA)
    new_doc.save()
    refresh()

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
    assert not APIDoc.exists('new_slug', field="._meta.slug")

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

def teardown_module():
    """ teardown any state that was previously setup.
    """
    if APIDoc.exists(MYDISEASE_ID):
        doc = APIDoc.get(MYDISEASE_ID)
        doc.delete()
