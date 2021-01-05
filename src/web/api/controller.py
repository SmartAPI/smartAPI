"""
Controllers for API doc addition
and API metadata operations
"""
import base64
import copy
import gzip
import json
import logging
import string
from datetime import datetime as dt
import jsonschema
import requests
import yaml
import sys
from collections import OrderedDict
from abc import ABC, abstractmethod

if sys.version_info.major >= 3 and sys.version_info.minor >= 6:
    from hashlib import blake2b
else:
    from pyblake2 import blake2b  # pylint: disable=import-error

from elasticsearch import RequestError
from elasticsearch_dsl import Q
from .model import APIDoc

logger = logging.getLogger(__name__)

# *****************************************************************************
# Validation schemas, tags
# *****************************************************************************

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

# *****************************************************************************
# Custom Exceptions
# *****************************************************************************

class RegistryError(Exception):
    """General API error"""

class ValidationError(RegistryError):
    """Error from metadata validation"""

class APIMetadataRegistrationError(RegistryError):
    """Error from failed doc addition"""

class APIRequestError(RegistryError):
    """Error from network requests"""

class SlugRegistrationError(RegistryError):
    """Error from failed slug update"""

# *****************************************************************************
# Helper Functions
# *****************************************************************************

def encode_raw(metadata):
    '''
        return encoded and compressed metadata
    '''
    _raw = json.dumps(metadata).encode('utf-8')
    _raw = base64.urlsafe_b64encode(gzip.compress(_raw)).decode('utf-8')
    return _raw

def decode_raw(raw, sorted=True, as_string=False):
    '''
        if sorted is True, the keys in the decoded dictionary will follow a defined order.
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

def get_api_metadata_by_url(url):

    try:
        res = requests.get(url, timeout=5)
    except requests.exceptions.RequestException as err:
        raise APIRequestError(f'Failed URL request: {str(err)}')
    if res.status_code != 200:
        raise APIRequestError(f'Failed URL request with status: {res.status_code}')

    try:
        metadata = res.json()
    except ValueError:
        try:
            metadata = yaml.load(res.text, Loader=yaml.SafeLoader)
        except (yaml.scanner.ScannerError, yaml.parser.ParserError) as err:
            raise APIRequestError(f'Invalid Format: {str(err)}')

    return metadata

# *****************************************************************************
# Metadata Validation
# *****************************************************************************

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
        except Exception:
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
            raise ValidationError('Version unknown or unsupported')
        try:
            jsonschema.validate(self.metadata, self.oas_schema)
        except jsonschema.ValidationError as e:
            err_msg = "'{}': {}".format('.'.join([str(x) for x in e.path]), e.message)
            raise ValidationError(err_msg)
        except Exception as e:
            raise ValidationError("Unexpected Validation Error: {} - {}".format(type(e).__name__, e))

        if self.schema_version == 'OAS3':
            try:
                jsonschema.validate(self.metadata, self.smartapi_schema)
            except jsonschema.ValidationError as e:
                err_msg = "'{}': {}".format('.'.join([str(x) for x in e.path]), e.message)
                raise ValidationError(err_msg)
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

# *****************************************************************************
# API Doc Controller
# *****************************************************************************

class APIDocController(ABC):

    def __init__(self, _metadata=None):
        self.metadata = _metadata

    @staticmethod
    def exists(_id):
        return APIDoc.exists(_id)

    @abstractmethod
    def save(cls, api_doc, user_name=None, **options):
        pass

    @staticmethod
    def from_dict(dic):
        if 'openapi' in dic:
            return V3Metadata(dic)
        if 'swagger' in dic:
            return V2Metadata(dic)

    @staticmethod
    def _get_api_doc(api_doc, with_meta=True, raw=False):
        if raw:
            doc = decode_raw(api_doc['~raw'])
        else:
            doc = api_doc
        if with_meta:
            doc["_meta"] = api_doc['_meta']
            doc["_id"] = api_doc["_id"]
        return doc

    @staticmethod
    def get_api(api_name, fields=[], with_meta=False, return_raw=True, from_=0):
        """
        Get one doc by id/slug
        """
        search = APIDoc.search()
        search.query = Q('bool', should=[Q('match', _id=api_name) | Q('term', _meta__slug=api_name)], minimum_should_match=1)

        if fields:
            search = search.source(includes=fields)

        if search.count() > 1:
            raise APIRequestError(f"No exact matches for '{api_name}' found: {search.count()} results")

        return APIDocController._get_api_doc(search[0], with_meta=with_meta, raw=return_raw)

    @staticmethod
    def get_all(fields=[], from_=0, size=10):
        """
        Returns a list of all docs in index.
        Each document is a dsl search hit that behaves like a dictionary
        """
        search = APIDoc.search()
        search = search[from_: from_ + size]

        if fields:
            search = search.source(includes=fields)
        return list(iter(search))

    @staticmethod
    def get_api_id_from_slug(slug):
        """
        Return ID of doc with exact match for slug provided

        Returns:
            doc ID for exact match
        """

        if not slug:
            raise RequestError('slug is required')
        search = APIDoc.search()
        search = search.query('term', _meta__slug__raw=slug)

        if not search.count() == 1:
            raise APIRequestError(f'Query for "{slug}" has {search.count()} results')

        return search[0].id

    @staticmethod
    def slug_is_available(slug):
        """
        Check if a slug is available

        Returns:
            Bool = exists
        """
        if not slug:
            raise RequestError('slug is required')
        res = APIDoc.slug_exists(slug)
        return res

    @staticmethod
    def validate_slug_name(slug_name):
        """
        Function that determines whether slug_name is a valid slug name

        Args:
            slug_name (str): new slug name

        Raises:
            SlugRegistrationError: detail slug registration msg
        """
        _valid_chars = string.ascii_letters + string.digits + "-_~"
        _slug = slug_name.lower()
        if _slug in ('www', 'dev', 'smart-api'):
            raise SlugRegistrationError(f"Slug name {slug_name} is reserved, please choose another")
        if not all([x in _valid_chars for x in _slug]):
            raise SlugRegistrationError(f"Slug name {slug_name} contains invalid characters")
        if APIDoc.slug_exists(slug=_slug):
            raise SlugRegistrationError(f"Slug name {slug_name} already exists")

    @staticmethod
    def get_tags(field=None, size=100):
        """
        perform aggregations on given field
        Used to generate list of tags and authors

        Args:
            field (str, optional): field name of doc. Defaults to None.
            size (int, optional): size returned. Defaults to 100.

        Returns:
            list of tags/authors name:occurrence
        """
        agg_name = 'field_values'

        res = APIDoc.aggregate(field=field, size=size, agg_name=agg_name)
        return res.to_dict()

    @staticmethod
    def delete(_id, user):
        """
        delete api with ID
        """
        doc = APIDoc.get(id=_id)
        _user = doc['_meta']['github_username']

        if user.get('login', None) != _user:
            raise APIRequestError("User '{}' is not the owner of API '{}'".format(user.get('login', None), _id))

        doc.delete()
        return _id

    def update_slug(self, _id, user, slug_name):
        """
        Update API doc slug name

        Args:
            _id (str): doc ID to be updated
            user (dict): user info of requester
            slug_name (str): new slug name

        Raises:
            SlugRegistrationError: detail slug registration msg

        Returns:
            msg with id._meta.slug and updated slug name
        """
        if not self.exists(_id):
            raise APIRequestError(f"API with id '{_id}' does not exist")

        i = self._doc.to_dict()
        _user = i.get('_meta', {}).get('github_username', '')

        if user.get('login', None) != _user:
            raise APIRequestError("User '{}' is not the owner of API '{}'".format(user.get('login', None), _id))

        self.validate_slug_name(slug_name)

        self._doc.update(id=_id, refresh=True, _meta={"slug": slug_name.lower()})
        return {"{}._meta.slug".format(_id): slug_name.lower()}

    def refresh_api(self, _id, user, test=False):
        """
        refresh the given API document object based on its saved metadata url

        Args:
            _id (str): ID of API doc
            user (dict): user info
            test : if test doc will not update to avoid conflict with unit test

        Returns:
            Dict with ID updated message
        """
        if not self.exists(_id):
            raise APIRequestError(f"API with id '{_id}' does not exist")

        api_doc = self._doc.to_dict()

        _meta = api_doc.get('_meta', {})

        res = get_api_metadata_by_url(_meta['url'])

        if res and isinstance(res, dict):
            _meta['timestamp'] = dt.now().isoformat()
            res['_meta'] = _meta
            if test:
                return {'test-updated': f"API with ID {_id} was refreshed"}
            self._doc.update(id=_id, refresh=True, **res['metadata'])
            return {'updated': f"API with ID {_id} was refreshed"}
        else:
            raise APIRequestError('Invalid input data.')

    def delete_slug(self, _id):
        """
        delete the slug of API _id.
        used in APIMetaDataHandler [DELETE]

        Args:
            _id (str): ID of doc
        """
        if not self.exists(_id):
            raise APIRequestError(f"API with id '{_id}' does not exist")

        self._doc.update(id=_id, refresh=True, _meta={'slug': ''})

        return f"slug deleted for {_id} was deleted"

class V3Metadata(APIDocController):

    def __init__(self, metadata):
        # get the major version of the schema type
        if metadata.get('openapi', False):
            self.schema_version = 'OAS' + metadata['openapi'].split('.')[0]
        else:
            self.schema_version = None
        # set the correct schema validation url
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

    def get_schema(self):
        schema = requests.get(self.schema_url).text
        if schema.startswith("export default "):
            schema = schema[len("export default "):]
        try:
            self.oas_schema = json.loads(schema)
        except Exception:
            self.oas_schema = yaml.load(schema, Loader=yaml.SafeLoader)
        self.smartapi_schema = requests.get(SMARTAPI_SCHEMA_URL).json()

    def validate_oas3(self):
        '''
        Validate against V3 OpenAPI schema
        '''
        if not self.schema_version or self.schema_version != "OAS3":
            raise ValidationError('Version unknown or not OAS3')
        try:
            jsonschema.validate(self.metadata, self.oas_schema)
        except jsonschema.ValidationError as e:
            err_msg = "'{}': {}".format('.'.join([str(x) for x in e.path]), e.message)
            raise ValidationError(err_msg)
        except Exception as e:
            raise ValidationError("Unexpected Validation Error: {} - {}".format(type(e).__name__, e))

    def validate_smartapi(self):
        '''
        Validate against SmartAPI schema
        '''
        try:
            jsonschema.validate(self.metadata, self.smartapi_schema)
        except jsonschema.ValidationError as e:
            err_msg = "'{}': {}".format('.'.join([str(x) for x in e.path]), e.message)
            raise ValidationError(err_msg)

    def encode_api_id(self, url):
        if not url:
            raise ValueError("Missing required _meta.url field.")
        return blake2b(url.encode('utf8'), digest_size=16).hexdigest()

    def convert_es(self):
        '''convert API metadata for ES indexing.'''
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
        # include compressed binary raw metadata as "~raw"
        _d["~raw"] = encode_raw(self.metadata)
        return _d

    def create_meta(self, url, user_name):
        """
        Add creation metadata
        """
        self._meta = {
            "github_username": user_name,
            'url': url,
            'timestamp': dt.now().isoformat()
        }

    def save(self, api_doc, user_name=None, **options):
        """
        Save an OpenAPI V3 document

        Returns saved API ID
        """
        dryrun = options.get('dryrun')
        overwrite = options.get('overwrite')
        url = options.get('url')

        self.validate_oas3()
        self.validate_smartapi()

        api_id = self.encode_api_id(url)
        doc_exists = self.exists(api_id)

        if doc_exists and not overwrite:
            raise APIMetadataRegistrationError('API Exists')
        if dryrun:
            raise APIMetadataRegistrationError('API is valid but this was only a test')

        self.create_meta(url, user_name)
        doc = APIDoc(meta={'id': api_id}, ** self.convert_es())
        doc.save()
        return {'_id': api_id}

class V2Metadata(APIDocController):

    def __init__(self, metadata):
        # get the major version of the schema type
        if metadata.get('swagger', False):
            self.schema_version = 'SWAGGER' + metadata['swagger'].split('.')[0]
        else:
            self.schema_version = None
        # set the correct schema validation url
        self.schema_url = SWAGGER2_SCHEMA_URL
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
        except Exception:
            self.oas_schema = yaml.load(schema, Loader=yaml.SafeLoader)
        self.smartapi_schema = requests.get(SMARTAPI_SCHEMA_URL).json()

    def encode_api_id(self, url):
        if not url:
            raise ValueError("Missing required _meta.url field.")
        return blake2b(url.encode('utf8'), digest_size=16).hexdigest()

    def validate(self):
        '''Validate against OpenAPI V3 schema'''
        if not self.schema_version or self.schema_version != "SWAGGER2":
            raise ValidationError('Version unknown or not SWAGGER2')
        try:
            jsonschema.validate(self.metadata, self.oas_schema)
        except jsonschema.ValidationError as e:
            err_msg = "'{}': {}".format('.'.join([str(x) for x in e.path]), e.message)
            raise ValidationError(err_msg)
        except Exception as e:
            raise ValidationError("Unexpected Validation Error: {} - {}".format(type(e).__name__, e))

        return {"valid": True, "v2": True}

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

        # include compressed binary raw metadata as "~raw"
        _d["~raw"] = encode_raw(self.metadata)
        return _d

    def save(self, api_doc, user_name=None, **options):
        """
        Save a Swagger V2 document

        Returns saved API ID
        """
        save_v2 = options.get('save_v2')
        dryrun = options.get('dryrun')
        overwrite = options.get('overwrite')
        url = options.get('url')

        api_doc['_meta'] = {
            "github_username": user_name,
            'url': url,
            'timestamp': dt.now().isoformat()
        }

        validation = self.validate()

        if validation.get('valid') is False:
            return validation
        if validation.get('v2') is True and not save_v2:
            raise APIMetadataRegistrationError('API is Swagger V2 which is not fully suppported')

        api_id = self.encode_api_id()
        doc_exists = self.exists(api_id)

        if doc_exists and not overwrite:
            raise APIMetadataRegistrationError('API Exists')
        if dryrun:
            raise APIMetadataRegistrationError('API is valid but this was only a test')

        doc = APIDoc(meta={'id': api_id}, ** self.convert_es())
        doc.save()
        return {'_id': api_id}
