import json
import os

import pytest

from controller.base import OpenAPI, Swagger

dirname = os.path.dirname(__file__)

with open(os.path.join(dirname, "swagger.json"), "r") as file:
    SWAGGER = json.load(file)

with open(os.path.join(dirname, "openapi.json"), "r") as file:
    OPENAPI = json.load(file)


def aligns(keys, reference):
    common = set(keys) & set(reference)
    keys = tuple(key for key in keys if key in common)
    refs = tuple(key for key in reference if key in common)
    return keys == refs


def test_swagger():
    swagger = Swagger(SWAGGER)
    assert tuple(swagger.keys())[: len(Swagger.KEYS)] == Swagger.KEYS
    swagger.validate()
    swagger["_metadata"] = {}
    swagger.data.move_to_end("_metadata", False)  # to front
    assert tuple(swagger.keys())[: len(Swagger.KEYS)] != Swagger.KEYS
    assert tuple(swagger.keys())[0] == "_metadata"
    swagger.order()
    assert tuple(swagger.keys())[: len(Swagger.KEYS)] == Swagger.KEYS
    with pytest.raises(ValueError):
        swagger.validate()  # _metadata is an invalid key
    assert tuple(swagger.keys()) != Swagger.KEYS
    swagger.clean()
    assert tuple(swagger.keys()) == Swagger.KEYS
    with pytest.raises(ValueError):
        # "paths" key is removed for ES indexing
        swagger.validate()


def test_openapi():
    openapi = OpenAPI(OPENAPI)
    assert aligns(openapi.keys(), OpenAPI.KEYS)
    openapi["_metadata"] = {}
    openapi.data.move_to_end("_metadata", False)  # to front
    assert tuple(openapi.keys())[0] == "_metadata"
    assert aligns(openapi.keys(), OpenAPI.KEYS)
    openapi.data.move_to_end("openapi")
    assert not aligns(openapi.keys(), OpenAPI.KEYS)
    openapi.order()
    assert aligns(openapi.keys(), OpenAPI.KEYS)
    with pytest.raises(ValueError):
        openapi.validate()  # _metadata is an invalid key
    del openapi["_metadata"]
    openapi.validate()
    assert tuple(openapi.keys()) != OpenAPI.KEYS
    assert isinstance(openapi["paths"], dict)
    assert "/gene" in openapi["paths"]
    assert "/query" in openapi["paths"]
    assert "/metadata" in openapi["paths"]
    openapi.transform()
    openapi.clean()
    assert aligns(openapi.keys(), OpenAPI.KEYS)
    assert not set(openapi.keys()) - set(OpenAPI.KEYS)
    assert isinstance(openapi["paths"], list)
    assert openapi["paths"][0]["path"] == "/gene"
    assert openapi["paths"][2]["path"] == "/metadata"
    assert openapi["paths"][4]["path"] == "/query"
    with pytest.raises(ValueError):
        # "paths" is transformed for ES indexing
        openapi.validate()
