import pytest

from web.api.controller import APIMetadata, ValidationError

transform_test_doc = {
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
    'paths': {
        "/metadata/fields": {
            "get": {
                "summary": "Get metadata about the data fields available from MyGene.info.",
                "responses": {
                    "200": {
                        "description": "MyGene.info metadata fields object"
                    }
                },
                "parameters": [
                    {
                        "schema": {
                            "type": "string"
                        },
                        "in": "query",
                        "name": "search",
                        "description": "Pass a search term to filter the available fields, e.g. \"search=clinvar\"."
                    },
                    {
                        "schema": {
                            "type": "string"
                        },
                        "in": "query",
                        "name": "prefix",
                        "description": "Pass a prefix string to filter the available fields, e.g. \"prefix=refseq\"."
                    },
                    {
                        "name": "callback",
                        "$ref": "#/components/parameters/callback"
                    }
                ]
            }
        },
    },
    "_meta": {
        "github_username": "marcodarko",
        "url": "https://raw.githubusercontent.com/marcodarko/api_exmaple/master/api.yml",
        "timestamp": "2020-12-01T15:17:45.862906+00:00",
        "ETag": "d178b8f1976d3aadd8bed151614445e5fc17cc9548e174dcebbc42a60eb086cf"
    },
}


# *****************************************************************************
# METADATA VALIDATOR AND TRANSFORM TESTS
# *****************************************************************************

def test_transform_paths():
    """
    Transform field 'paths' for optimal performance on ES
    """
    metadata = APIMetadata(transform_test_doc)
    transformed = metadata.convert_es()
    first_item = transformed.get('paths')[0]
    assert first_item.get('path') and first_item.get('pathitem')

def test_validate_doc():
    """
    Validate doc against specification schema
    """
    valid = False
    try:
        metadata = APIMetadata(transform_test_doc)
        validation = metadata.validate()
        valid = validation.get('valid')
    except ValidationError:
        valid = False
    assert valid is True
