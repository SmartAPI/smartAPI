'''
Validate and transform SmartAPI/OpenAPI v3 metadata for indexing
'''
import copy
import json
import base64
import gzip
from collections import OrderedDict

import requests
import yaml
import jsonschema


SMARTAPI_SCHEMA_URL = 'https://raw.githubusercontent.com/WebsmartAPI/smartAPI-editor/master/node_modules_changes/opanapi.json'
METADATA_KEY_ORDER = ['openapi', 'info', 'servers', 'externalDocs', 'tags', 'security', 'paths', 'components']


def encode_raw(metadata):
    '''return encoded and compressed metadata'''
    _raw = json.dumps(metadata).encode('utf-8')
    _raw = base64.urlsafe_b64encode(gzip.compress(_raw)).decode('utf-8')
    return _raw


def decode_raw(raw, sorted=True):
    '''if sorted is True, the keys in the decoded dictionary will follow
       a defined order.
    '''
    _raw = gzip.decompress(base64.urlsafe_b64decode(raw)).decode('utf-8')
    d = json.loads(_raw)
    if sorted:
        d2 = OrderedDict()
        for key in METADATA_KEY_ORDER:
            if key in d:
                d2[key] = d[key]
        for key in d:
            if key not in d2:
                d2[key] = d[key]
        return d2
    else:
        return d


def get_api_metadata_by_url(url, as_string=False):
    try:
        res = requests.get(url)
    except requests.exceptions.Timeout:
        return {"success": False, "error": "URL request is timeout."}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "URL request had a connection error."}
    if res.status_code != 200:
        return {"success": False, "error": "URL request returned {}.".format(res.status_code)}
    else:
        if as_string:
            return res.text
        else:
            try:
                metadata = res.json()
            except json.JSONDecodeError:
                try:
                    metadata =yaml.load(res.text)
                except (yaml.scanner.ScannerError,
                        yaml.parser.ParserError):
                    return {"success": False,
                            "error": "Not a valid JSON or YAML format."}
            return metadata


class APIMetadata:
    def __init__(self, metadata):
        self.schema = self.get_schema()
        self.metadata = metadata
        self._meta = self.metadata.pop('_meta', {})

    def get_schema(self):
        return json.loads(requests.get(SMARTAPI_SCHEMA_URL).text)

    def validate(self):
        '''Validate API metadata against JSON Schema.'''
        try:
            jsonschema.validate(self.metadata, self.schema)
        except jsonschema.ValidationError as e:
            return {"valid": False, "error": e.message}
        return {"valid": True}

    def _encode_raw(self):
        '''return encoded and compressed metadata'''
        _raw = json.dumps(self.metadata).encode('utf-8')
        _raw = base64.urlsafe_b64encode(gzip.compress(_raw)).decode('utf-8')
        return _raw

    def convert_es(self):
        '''convert API metadata for ES indexing.'''
        _d = copy.copy(self.metadata)
        _d['_meta'] = self._meta

        # convert paths to a list of each path item
        _paths = []
        for path in _d['paths']:
            _paths.append({
                "path": path,
                "pathitem": _d['paths'][path]
            })
        _d['paths'] = _paths

        #include compressed binary raw metadata as "~raw"
        _d["~raw"] = encode_raw(self.metadata)
        return _d
