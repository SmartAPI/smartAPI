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

import sys
if sys.version_info.major >= 3 and sys.version_info.minor >= 6:
    from hashlib import blake2b
else:
    from pyblake2 import blake2b


# Official oas3 json schema for validation is still in-development.
# For now we us this updated oas3-schema from swagger-editor
OAS3_SCHEMA_URL = 'https://raw.githubusercontent.com/swagger-api/swagger-editor/v3.6.1/src/plugins/validate-json-schema/structural-validation/oas3-schema.js'
SWAGGER2_SCHEMA_URL = 'https://raw.githubusercontent.com/swagger-api/swagger-editor/v3.6.1/src/plugins/validate-json-schema/structural-validation/swagger2-schema.js'

# List of root keys that should be indexed in version 2 schema
SWAGGER2_INDEXED_ITEMS = ['info', 'tags', 'swagger', 'host', 'basePath']

# list of major versions of schema that we support
SUPPORTED_SCHEMA_VERSIONS = ['SWAGGER2', 'OAS3']

# This is a separate schema for SmartAPI extensions only
SMARTAPI_SCHEMA_URL = 'https://raw.githubusercontent.com/SmartAPI/smartAPI-Specification/OpenAPI.next/schemas/smartapi_schema.json'
METADATA_KEY_ORDER = ['openapi', 'info', 'servers', 'externalDocs', 'tags', 'security', 'paths', 'components']


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


def get_api_metadata_by_url(url, as_string=False):
    try:
        res = requests.get(url, timeout=5)
    except requests.exceptions.Timeout:
        return {"success": False, "error": "URL request is timeout."}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "URL request had a connection error."}
    except requests.exceptions.RequestException:
        return {"success": False, "error": "Failed to make the request to this URL."}
    if res.status_code != 200:
        return {"success": False, "error": "URL request returned {}.".format(res.status_code)}
    else:
        if as_string:
            return res.text
        else:
            try:
                metadata = res.json()
            # except json.JSONDecodeError:   # for py>=3.5
            except ValueError:               # for py<3.5
                try:
                    metadata = yaml.load(res.text)
                except (yaml.scanner.ScannerError,
                        yaml.parser.ParserError):
                    return {"success": False,
                            "error": "Not a valid JSON or YAML format."}
            return metadata


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
            self._meta['ETag'] = requests.get(self._meta['url']).headers.get('ETag', 'I').strip('W/"')
        except:
            pass
        if self.schema_version == 'SWAGGER2':
            self._meta['swagger_v2'] = True

    def get_schema(self):
        schema = requests.get(self.schema_url).text
        if schema.startswith("export default "):
            schema = schema[len("export default "):]
        self.oas_schema = json.loads(schema)
        self.smartapi_schema = requests.get(SMARTAPI_SCHEMA_URL).json()

    def encode_api_id(self):
        x = self._meta.get('url', None)
        if not x:
            raise ValueError("Missing required _meta.url field.")
        return blake2b(x.encode('utf8'), digest_size=16).hexdigest()

    def validate(self, raise_error_on_v2=True):
        '''Validate API metadata against JSON Schema.'''
        if not self.schema_version or self.schema_version not in SUPPORTED_SCHEMA_VERSIONS:
            return {"valid": False, "error": "Unsupported schema version '{}'.  Supported versions are: '{}'.".format(self.schema_version, SUPPORTED_SCHEMA_VERSIONS)}
        if raise_error_on_v2 and self.schema_version == 'SWAGGER2':
            return {"valid": False, "error": "Found a v2 swagger schema, please convert to v3 for fullest functionality or click the checkbox to proceed with v2 anyway.", "swagger_v2": True}
        try:
            jsonschema.validate(self.metadata, self.oas_schema)
        except jsonschema.ValidationError as e:
            err_msg = "'{}': {}".format('.'.join([str(x) for x in e.path]), e.message)
            return {"valid": False, "error": "[{}] ".format(self.schema_version) + err_msg}
        except Exception as e:
            return {"valid": False, "error": "Unexpected Validation Error: {}".format(e)}

        if self.schema_version == 'OAS3':
            try:
                jsonschema.validate(self.metadata, self.smartapi_schema)
            except jsonschema.ValidationError as e:
                err_msg = "'{}': {}".format('.'.join([str(x) for x in e.path]), e.message)
                return {"valid": False, "error": "[SmartAPI] " + err_msg}
            _warning = ""
            _ret = {"valid": True}
        else:
            _warning = "No SmartAPI extensions supported on Swagger/OpenAPI version 2"
            _ret = {"valid": True, "_warning": _warning, "swagger_v2": True}
        return _ret

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

        #include compressed binary raw metadata as "~raw"
        _d["~raw"] = encode_raw(self.metadata)
        return _d
