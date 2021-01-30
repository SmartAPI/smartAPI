import os

import pytest
from utils import decoder

dirname = os.path.dirname(__file__)

with open(os.path.join(dirname, 'doc_mydisease.yaml'), 'rb') as file:
    YAML = file.read()

with open(os.path.join(dirname, 'doc_mydisease.json'), 'rb') as file:
    JSON = file.read()

with open(os.path.join(dirname, 'doc_javascript.ts'), 'rb') as file:
    JSTS = file.read()

with open(os.path.join(dirname, 'doc_swagger2.js'), 'rb') as file:
    SWAGGER = file.read()


def _ok(doc):
    assert "openapi" in doc
    assert "info" in doc
    assert "paths" in doc


def test_yaml_good():
    _ok(decoder.to_yaml(YAML))
    # practically uncommon
    assert decoder.to_yaml(b'{}') == {}
    # but JSON is a subset of YAML
    _ok(decoder.to_yaml(JSON))


def test_yaml_bad():
    with pytest.raises(TypeError):  # NOTE TypeError
        decoder.to_yaml(b'')
    with pytest.raises(TypeError):
        decoder.to_yaml(b'/\\')
    with pytest.raises(ValueError):
        decoder.to_yaml(JSTS)


def test_json_good():
    _ok(decoder.to_json(JSON))
    assert decoder.to_json(b'{}') == {}


def test_json_bad():
    with pytest.raises(TypeError):
        decoder.to_json(b'[]')
    with pytest.raises(ValueError):  # NOTE ValueError
        decoder.to_json(b'')
    with pytest.raises(ValueError):
        decoder.to_json(YAML)
    with pytest.raises(ValueError):
        decoder.to_json(JSTS)


def test_auto_good():
    _ok(decoder.to_dict(YAML))
    _ok(decoder.to_dict(JSON))
    _ok(decoder.to_dict(JSTS))  # NOTE Javascript Only Supported Here

    _ok(decoder.to_dict(JSON, 'json'))
    _ok(decoder.to_dict(JSON, ctype='application/json'))
    _ok(decoder.to_dict(JSON, ctype='application/JSON'))
    _ok(decoder.to_dict(JSON, 'json', 'application/json'))
    _ok(decoder.to_dict(JSON, ctype='application/json; charset=utf-8'))

    _ok(decoder.to_dict(YAML, 'yml'))
    _ok(decoder.to_dict(YAML, 'yaml'))
    _ok(decoder.to_dict(YAML, ctype='application/yaml'))
    _ok(decoder.to_dict(YAML, ctype='application/YAML'))
    _ok(decoder.to_dict(YAML, 'yaml', 'application/yaml'))
    _ok(decoder.to_dict(YAML, ctype='application/yaml; charset=utf-8'))


def test_auto_bad():
    with pytest.raises(TypeError):  # NOTE TypeError
        decoder.to_dict(b'')
    with pytest.raises(TypeError):
        decoder.to_dict(b'[]')
    with pytest.raises(TypeError):
        decoder.to_dict(b'/\\')
    with pytest.raises(ValueError):
        decoder.to_dict(YAML, 'json')
    with pytest.raises(ValueError):
        decoder.to_dict(YAML, ctype='application/json')


def test_javascript():
    # intentionally test this because
    # we rely on it in the application
    doc = decoder.to_dict(SWAGGER)
    assert doc["id"] == "http://swagger.io/v2/schema.json#"
    assert doc["type"] == "object"
    assert "$schema" in doc
    assert "required" in doc
