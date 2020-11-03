'''
Validate and transform SmartAPI/OpenAPI v3 metadata for indexing
'''
import base64
import copy
import gzip
import json
import sys
from collections import OrderedDict

import jsonschema
import requests
import yaml

if sys.version_info.major >= 3 and sys.version_info.minor >= 6:
    from hashlib import blake2b
else:
    from pyblake2 import blake2b  # pylint: disable=import-error


# Official oas3 json schema for validation is still in-development.
# For now we us this updated oas3-schema from swagger-editor
OAS3_SCHEMA_URL = 'https://raw.githubusercontent.com/swagger-api/swagger-editor/v3.7.1/src/plugins/json-schema-validator/oas3-schema.yaml'
SWAGGER2_SCHEMA_URL = 'https://raw.githubusercontent.com/swagger-api/swagger-editor/v3.6.1/src/plugins/validate-json-schema/structural-validation/swagger2-schema.js'

# List of root keys that should be indexed in version 2 schema
SWAGGER2_INDEXED_ITEMS = ['info', 'tags', 'swagger', 'host', 'basePath']

# list of major versions of schema that we support
SUPPORTED_SCHEMA_VERSIONS = ['SWAGGER2', 'OAS3']

# This is a separate schema for SmartAPI extensions only
SMARTAPI_SCHEMA_URL = 'https://raw.githubusercontent.com/SmartAPI/smartAPI-Specification/OpenAPI.next/schemas/smartapi_schema.json'
METADATA_KEY_ORDER = ['openapi', 'info', 'servers',
                      'externalDocs', 'tags', 'security', 'paths', 'components']


def encode_raw(metadata):
    '''return encoded and compressed metadata'''
    _raw = json.dumps(metadata).encode('utf-8')
    _raw = base64.urlsafe_b64encode(gzip.compress(_raw)).decode('utf-8')
    return _raw


def decode_raw(raw, sorted=True, as_string=False):
    '''if sorted is True, the keys in the decoded dictionary will follow
       a defined order.
    '''
    _raw = gzip.decompress(base64.urlsafe_b64decode(raw)).decode('utf-8')
    if as_string:
        return _raw
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


def polite_requests(url, head=False):
    try:
        if head:
            res = requests.head(url, timeout=5)
        else:
            res = requests.get(url, timeout=5)
    except requests.exceptions.Timeout:
        return {"because": "URL request is timeout."}
    except requests.exceptions.ConnectionError:
        return {"because": "URL request had a connection error."}
    except requests.exceptions.RequestException:
        return {"because": "Failed to make the request to this URL."}
    if res.status_code != 200:
        return {"because": "URL request returned {}.".format(res.status_code)}
    return {"success": True, "response": res}


def get_api_metadata_by_url(url, as_string=False):

    _res = polite_requests(url)
    if 'success' in _res:
        res = _res.get('response')
        if as_string:
            return res.text
        else:
            try:
                metadata = res.json()
            except ValueError:
                try:
                    metadata = yaml.load(res.text, Loader=yaml.SafeLoader)
                except (yaml.scanner.ScannerError, yaml.parser.ParserError):
                    return {"because": "Not a valid JSON or YAML format."}
            return {'metadata': metadata}
    else:
        return _res


class APIMetadata:
    def __init__(self, metadata):
        # get the major version of the schema type
        if metadata.get('openapi', False):
            self.schema_version = 'OAS' + metadata['openapi'].split('.')[0]
        elif metadata.get('swagger', False):
            self.schema_version = 'SWAGGER' + metadata['swagger'].split('.')[0]
        else:
            self.schema_version = None
        # set the correct schema validation url
        if self.schema_version == 'SWAGGER2':
            self.schema_url = SWAGGER2_SCHEMA_URL
        else:
            self.schema_url = OAS3_SCHEMA_URL
        self.get_schema()
        self.metadata = metadata
        self._meta = self.metadata.pop('_meta', {})
        try:
            self._meta['ETag'] = requests.get(
                self._meta['url']).headers.get(
                'ETag', 'I').strip('W/"')
        except BaseException:
            pass
        if self.schema_version == 'SWAGGER2':
            self._meta['swagger_v2'] = True

    def get_schema(self):
        schema = requests.get(self.schema_url).text
        if schema.startswith("export default "):
            schema = schema[len("export default "):]
        try:
            self.oas_schema = json.loads(schema)
        except:
            self.oas_schema = yaml.load(schema, Loader=yaml.SafeLoader)
        self.smartapi_schema = requests.get(SMARTAPI_SCHEMA_URL).json()

    def encode_api_id(self):
        x = self._meta.get('url', None)
        if not x:
            raise ValueError("Missing required _meta.url field.")
        return blake2b(x.encode('utf8'), digest_size=16).hexdigest()

    def validate(self):
        '''Validate API metadata against JSON Schema.'''
        if not self.schema_version or self.schema_version not in SUPPORTED_SCHEMA_VERSIONS:
            return {'because': 'Version unknown or unsupported'}
        try:
            jsonschema.validate(self.metadata, self.oas_schema)
        except jsonschema.ValidationError as e:
            err_msg = "'{}': {}".format('.'.join([str(x) for x in e.path]), e.message)
            return {'because': err_msg}
        except Exception as e:
            return {"because": "Unexpected Validation Error: {} - {}".format(type(e).__name__, e)}

        if self.schema_version == 'OAS3':
            try:
                jsonschema.validate(self.metadata, self.smartapi_schema)
            except jsonschema.ValidationError as e:
                err_msg = "'{}': {}".format('.'.join([str(x) for x in e.path]), e.message)
                return {'because': err_msg}
            return {"valid": True}
        else:
            return {"valid": True, "v2": True}

    def _encode_raw(self):
        '''return encoded and compressed metadata'''
        _raw = json.dumps(self.metadata).encode('utf-8')
        _raw = base64.urlsafe_b64encode(gzip.compress(_raw)).decode('utf-8')
        return _raw

    def convert_es(self):
        '''convert API metadata for ES indexing.'''

        if self.schema_version == 'OAS3':
            _d = copy.copy(self.metadata)
            _d['_meta'] = self._meta
            # convert paths to a list of each path item
            _paths = []
            for path in _d.get('paths', []):
                _paths.append({
                    "path": path,
                    "pathitem": _d['paths'][path]
                })
            if _paths:
                _d['paths'] = _paths
        else:
            # swagger 2 or other, only index limited fields
            _d = {"_meta": self._meta}
            for key in SWAGGER2_INDEXED_ITEMS:
                if key in self.metadata:
                    _d[key] = self.metadata[key]

        # include compressed binary raw metadata as "~raw"
        _d["~raw"] = encode_raw(self.metadata)
        return _d
