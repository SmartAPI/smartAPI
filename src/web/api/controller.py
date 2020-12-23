"""
Controllers for API doc addition
and API metadata operations

[APIHandler] (C)
add - save doc

[APIMetaDataHandler] (R.U.D)
get_api - get doc by name/slug
refresh_api - refresh api metadata
delete_slug - delete registered slug
update - save new slug
validate_slug_name - check slugname

Raises:
    ValidationError: any schema validation error
    APIMetadataRegistrationError: error during POST
    SlugRegistrationError: error during slug setup
    APIRequestError: metadata url request error
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

if sys.version_info.major >= 3 and sys.version_info.minor >= 6:
    from hashlib import blake2b
else:
    from pyblake2 import blake2b  # pylint: disable=import-error

from elasticsearch import RequestError
from elasticsearch_dsl import Q
from .model import API_Doc

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
        _res = requests.get(url, timeout=5)
    except requests.exceptions.RequestException as err:
        raise APIRequestError(f'Failed URL request: {str(err)}')
    if res.status_code != 200:
        raise APIRequestError(f'Failed URL request with status: {res.status_code}')

    res = _res.get('response')

    try:
        metadata = res.json()
    except ValueError:
        try:
            metadata = yaml.load(res.text, Loader=yaml.SafeLoader)
        except (yaml.scanner.ScannerError, yaml.parser.ParserError) as err:
            raise APIRequestError(f'Invalid Format: {str(err)}')

    return metadata

# *****************************************************************************
# Validation Controller
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
# API Metadata Controller
# *****************************************************************************

class APIDocController:

    def __init__(self, _id):
        self._doc = API_Doc.get(id=_id)
        
    @staticmethod
    def exists(_id):
        # TODO
        return True
    
    @staticmethod
    def add(api_doc, user_name=None, **options):
        """
        APIMetadata Class validates doc for supported OAS3 or V2 (warning)
        and generates an id based on source url
        Check if document exists then
        Save Doc if passes all checks

        Args:
            api_doc (dict): [API metadata]
            save_v2 (bool, optional): [save outdated version]. Defaults to False.
            overwrite (bool, optional): [overwrite existing doc]. Defaults to False.
            user_name (str, optional): [user.login]. Defaults to None.
            dryrun (bool, optional): [test registration]. Defaults to False.

        Returns:
            Returns generated API ID if this operation resulted in a new document being saved.
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
        metadata = APIMetadata(api_doc)
        validation = metadata.validate()

        if validation.get('valid') is False:
            return validation
        if validation.get('v2') is True and not save_v2:
            raise APIMetadataRegistrationError('API is Swagger V2 which is not fully suppported')

        api_id = metadata.encode_api_id()
        doc_exists = API_Doc.exists(api_id)

        if doc_exists and not overwrite:
            raise APIMetadataRegistrationError('API Exists')
        if dryrun:
            raise APIMetadataRegistrationError('API is valid but this was only a test')

        doc = API_Doc(meta={'id': api_id}, ** metadata.convert_es())
        doc.save()
        return {'_id': api_id}

    @staticmethod
    def get_api(api_name, fields=None, with_meta=True, return_raw=False, size=None, from_=0):
        """
        Get one doc by id/slug

        Args:
            api_name (str): id,name, or slug
            fields (list, optional): fields to return if not all
            with_meta (bool, optional): Return _meta field. Defaults to True.
            return_raw (bool, optional): return raw. Defaults to False.
            size (int, optional): size of results. Defaults to None.
            from_ (int, optional): start of returned results. Defaults to 0.
        Raises:
            ValueError: invalid input

        Returns:
            One API doc with metadata by default.
        """

        def _get_hit_object(hit):
            """[summary]

            Args:
                hit (list): ES response, list of hits

            Returns:
                dict: extracted doc dict
            """
            obj = hit.get('fields', hit.get('_source', {}))
            if '_id' in hit:
                obj['_id'] = hit['_id']
            return obj

        def _get_api_doc(api_doc, with_meta=True):
            doc = decode_raw(api_doc.get('~raw', ''))
            if with_meta:
                doc["_meta"] = api_doc.get('_meta', {})
                doc["_id"] = api_doc["_id"]
            return doc

        s = API_Doc.search()
        if not fields:
            fields = ['_all']

        s.source(includes=fields)
        s.query = Q('bool', should=[Q('match', _id=api_name) | Q('term', _meta__slug=api_name)], minimum_should_match=1)

        res = s.execute().to_dict()
        if return_raw:
            return res
        res = [_get_hit_object(d) for d in res['hits']['hits']]
        if not return_raw:
            try:
                res = [_get_api_doc(x, with_meta=with_meta) for x in res]
            except ValueError as e:
                res = {'success': False, 'error': str(e)}
        if len(res) == 1:
            res = res[0]
        return res

    @staticmethod
    def get_all(fields=None, from_=0):

        def _get_hit_object(hit):
            """[summary]

            Args:
                hit (list): ES response, list of hits

            Returns:
                dict: extracted doc dict
            """
            obj = hit.get('fields', hit.get('_source', {}))
            if '_id' in hit:
                obj['_id'] = hit['_id']
            return obj

        s = API_Doc.search()
        total = s.count()
        start = 0
        if from_:
            start = from_
        s = s[start:total]
        s.source(includes=fields)

        res = s.execute().to_dict()
        res = [_get_hit_object(d) for d in res['hits']['hits']]
        return res

    @staticmethod
    def get_api_id_from_slug(slug):
        """
        Return ID of doc with exact match for slug provided

        Args:
            slug (str): slug name

        Raises:
            RequestError: multiple hits or error fetching

        Returns:
            [str]: doc ID for exact match
        """

        if not slug:
            raise RequestError('slug is required')
        s = API_Doc.search()
        s = s.query('term', _meta__slug=slug)
        response = s.execute()

        if not response.hits.total.value == 1:
            raise APIRequestError(f'Query for "{slug}" has {response.hits.total.value} results')

        doc = response.hits[0]
        return doc.id

    @staticmethod
    def slug_is_available(slug):
        """
        Check if a slug is available

        Args:
            slug (str): slug name to be checked

        Raises:
            RequestError: slug was not provided

        Returns:
            Bool = exists
        """
        if not slug:
            raise RequestError('slug is required')
        res = API_Doc.slug_exists(slug)
        return res

    @staticmethod
    def validate_slug_name(slug_name):
        """
        Function that determines whether slug_name is a valid slug name

        Args:
            slug_name (str): new slug name

        Raises:
            SlugRegistrationError: detail slug registration msg

        Returns:
            True if available
        """
        _valid_chars = string.ascii_letters + string.digits + "-_~"
        _slug = slug_name.lower()
        if _slug in ('www', 'dev', 'smart-api'):
            raise SlugRegistrationError(f"Slug name {slug_name} is reserved, please choose another")
        if not all([x in _valid_chars for x in _slug]):
            raise SlugRegistrationError(f"Slug name {slug_name} contains invalid characters")
        if API_Doc.slug_exists(slug=_slug):
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

        res = API_Doc.aggregate(field=field, size=size, agg_name=agg_name)
        return res.to_dict()

    def delete(self, _id, user):
        """
        delete api with ID
        """
        if not self._doc.exists(_id):
            raise APIRequestError("API with id '{}' does not exist".format(_id))

        doc = self._doc.get(id=_id).to_dict()
        _user = doc.get('_meta', {}).get('github_username', '')

        if user.get('login', None) != _user:
            raise APIRequestError("User '{}' is not the owner of API '{}'".format(user.get('login', None), _id))

        self._doc.delete(id=_id)
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
        if not self._doc.exists(_id):
            raise APIRequestError("Could not retrieve API '{}' to set slug name".format(_id))

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
        if not API_Doc.exists(_id):
            raise APIRequestError(f"Could not retrieve API '{_id}' to delete slug name")

        self._doc.update(id=_id, refresh=True, _meta={'slug': ''})

        return f"slug deleted for {_id} was deleted"
