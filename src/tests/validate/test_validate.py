import os

import pytest

from controller.base import openapis, swaggers, validate

dirname = os.path.dirname(__file__)

with open(os.path.join(dirname, "openapi-pass.json"), "rb") as file:
    PASS_OPENAPI = file.read()

with open(os.path.join(dirname, "openapi3.1-pass.json"), "rb") as file:
    PASS_OPENAPI31 = file.read()

with open(os.path.join(dirname, "openapi3.1-fail.json"), "rb") as file:
    FAIL_OPENAPI31 = file.read()

with open(os.path.join(dirname, "swagger-pass.json"), "rb") as file:
    PASS_SWAGGER = file.read()

with open(os.path.join(dirname, "x-translator-pass.json"), "rb") as file:
    PASS_TRANSLATOR = file.read()

with open(os.path.join(dirname, "x-translator-fail-1.yml"), "rb") as file:
    FAIL_TRANSLATOR_1 = file.read()

with open(os.path.join(dirname, "x-translator-fail-2.yml"), "rb") as file:
    FAIL_TRANSLATOR_2 = file.read()


def test_01():
    validate(PASS_OPENAPI, {"openapi": openapis["openapi_v3.0"]})
    validate(PASS_OPENAPI, openapis)


def test_02():
    validate(PASS_TRANSLATOR, {"openapi": openapis["openapi_v3.0"]})
    validate(PASS_TRANSLATOR, {"x-translator": openapis["x-translator"]})
    validate(PASS_TRANSLATOR, openapis)


def test_03():
    validate(FAIL_TRANSLATOR_1, {"openapi": openapis["openapi_v3.0"]})
    with pytest.raises(ValueError):
        validate(FAIL_TRANSLATOR_1, openapis)


def test_04():
    validate(FAIL_TRANSLATOR_2, {"openapi": openapis["openapi_v3.0"]})
    with pytest.raises(ValueError):
        validate(FAIL_TRANSLATOR_2, openapis)


def test_05():
    validate(PASS_SWAGGER, swaggers)
    with pytest.raises(ValueError):
        validate(PASS_SWAGGER, openapis)
    with pytest.raises(ValueError):
        validate(PASS_OPENAPI, swaggers)

def test_06():
    validate(PASS_OPENAPI31, {"openapi": openapis["openapi_v3.1"]})
    validate(PASS_OPENAPI31, openapis)

def test_07():
    with pytest.raises(ValueError):
        validate(FAIL_OPENAPI31, {"openapi": openapis["openapi_v3.1"]})
    with pytest.raises(ValueError):
        validate(FAIL_OPENAPI31, openapis)

