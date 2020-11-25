"""
Controller for API docs

[APIHandler]
add - save doc

[APIMetaDataHandler]
get_api - get doc by name/slug
refresh_api - refresh api metadata
delete_slug - delete registered slug
update - save new slug
    _validate_slug_name - check slugname

[ValueSuggestionHandler]
get_tags - get list of tags/authors
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

if sys.version_info.major >= 3 and sys.version_info.minor >= 6:
    from hashlib import blake2b
else:
    from pyblake2 import blake2b  # pylint: disable=import-error

from elasticsearch import RequestError
from elasticsearch_dsl import Q
from ..model.api_doc import API_Doc

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

class ValidationError(Exception):
    pass

class APIMetadataRegistrationError(Exception):
    pass

class ESIndexingError(Exception):
    pass

class APIRequestError(Exception):
    pass

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

def polite_requests(url, head=False):
    """
        Return requested data from url as json/yaml
    """
    try:
        if head:
            res = requests.head(url, timeout=5)
        else:
            res = requests.get(url, timeout=5)
    except requests.exceptions.Timeout:
        raise APIRequestError('URL request is timeout')
    except requests.exceptions.ConnectionError:
        raise APIRequestError('URL request connection error')
    except requests.exceptions.RequestException:
        raise APIRequestError('Failed to make the request to this URL')
    if res.status_code != 200:
        raise APIRequestError(f'URL request returned {res.status_code}')
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
                    raise APIRequestError('Not a valid JSON or YAML format')
            return {'metadata': metadata}
    else:
        return _res

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

# *****************************************************************************
# API Metadata Controller
# *****************************************************************************

class APIDocController:

    def __init__(self, _id=None):
        doc = API_Doc()
        self._doc = doc.get(id=_id)

    @staticmethod
    def add(api_doc, user_name=None, **options):
        # def add(api_doc, save_v2=False, overwrite=False, user_name=None, dryrun=False, url=None):
        """
        APIMetadata Class validates doc for supported OAS3 or V2 (warning)
        and generates an id based on source url
        Check if document exists then
        Error details will be returned in 'because' field
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
        try:
            doc = API_Doc(meta={'id': api_id}, ** metadata.convert_es())
            doc.save()
        except RequestError as e:
            raise ESIndexingError(str(e))
        else:
            return {'_id': api_id}

    @staticmethod
    def get_api(api_name, fields=None, with_meta=True, return_raw=False, size=None, from_=0):
        """
        Used by Swagger UI to get doc metadata
        Used to get one specific doc by id/name/slug or get all

        Args:
            api_name (str): id,name, or slug
            fields (list, optional): fields to return if not all
            with_meta (bool, optional): Return _meta field. Defaults to True.
            return_raw (bool, optional): return raw. Defaults to False.
            size (int, optional): size of results. Defaults to None. No longer used.
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

        # client = Elasticsearch()
        # s = Search(using=client)
        s = API_Doc.search()
        # change to higher level client
        if not fields:
            fields = ['_all']

        if api_name == 'all':
            total = s.count()
            start = 0
            if from_:
                start = from_
            s = s[start:total]
            s.source(includes=fields)
        else:
            s.source(includes=fields)
            s.query = Q('bool', should=[Q('match', _id=api_name) | Q('term', _meta__slug=api_name)], minimum_should_match=1)
        res = s.execute().to_dict()
        if return_raw == '2':
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

    def get_tags(field=None, size=100):
        """
        perform aggregations on given field
        Used to generate list of tags and authors

        Args:
            field (str, optional): field name of doc. Defaults to None.
            size (int, optional): size returned. Defaults to 100.

        Returns:
            list of tags/authors name:occurrence or false
        """
        agg_name = 'field_values'
        res = API_Doc.aggregate(field=field, size=size, agg_name=agg_name)
        if res:
            return res.to_dict()
        else:
            return False

    def delete(self, _id, user):
        """
        delete api by current user
        refresh index after deletion and return true

        Args:
            _id (str): ID of doc
            user (str): user info of requester

        Returns:
            Success res if successful
        """
        doc = API_Doc.get(id=_id).to_dict()
        _user = doc.get('_meta', {}).get('github_username', '')

        if user.get('login', None) != _user:
            return {"because": "User '{}' is not the owner of API '{}'".format(user.get('login', None), _id)}

        self._doc.delete(id=_id)
        return {"deleted": True}

    def update(self, _id, user, slug_name):
        """
        Update API doc slug name

        Args:
            _id (str): doc ID to be updated
            user (dict): user info of requester
            slug_name (str): new slug name

        Raises:
            HTTPError: Doc does not exist
            HTTPError: User is not owner of doc
            HTTPError: General error parsing request

        Returns:
            Success res if updated
        """
        if not API_Doc.exists(_id):
            return {'because': "Could not retrieve API '{}' to set slug name".format(_id)}

        i = API_Doc.get(id=_id).to_dict()
        _user = i.get('_meta', {}).get('github_username', '')

        # Make sure this is the correct user
        if user.get('login', None) != _user:
            return {'because': "User '{}' is not the owner of API '{}'".format(user.get('login', None), _id)}

        # validate the slug name
        validation = self._validate_slug_name(slug_name=slug_name)

        if 'success' in validation:
            try:
                doc = API_Doc()
                doc = doc.get(id=_id)
                doc.update(id=_id, refresh=True, _meta={"slug": slug_name.lower()})
            except Exception as exc:
                return {'because': "[Err]" + str(exc)}
                # raise HTTPError(500, reason=str(exc))
            else:
                return {"{}._meta.slug".format(_id): slug_name.lower()}
        else:
            return validation

    def _validate_slug_name(self, slug_name):
        """
        Function that determines whether slug_name is a valid slug name

        Args:
            slug_name (str): new slug name

        Raises:
            HTTPError: slug is a reserved word
            HTTPError: slug is not correct length
            HTTPError: slug has invalid characters

        Returns:
            True if available
        """
        _valid_chars = string.ascii_letters + string.digits + "-_~"
        _slug = slug_name.lower()
        if _slug in ['www', 'dev', 'smart-api']:
            return {'because': f"Slug name {slug_name} is reserved, please choose another"}
        if len(_slug) < 4 or len(_slug) > 50:
            return {'because': f"Slug name {slug_name} must be between 4 and 50 chars"}
        if not all([x in _valid_chars for x in _slug]):
            return {'because': f"Slug name {slug_name} contains invalid characters"}
        if API_Doc.slug_exists(slug=_slug):
            return {'because': f"Slug name {slug_name} already exists"}
        return {'success': True}

    def refresh_api(self, _id, user):
        """
        refresh the given API document object based on its saved metadata url

        Args:
            _id (str): ID of API doc
            user (dict): user info

        Returns:
            Bool = updated?
        """

        api_doc = self._doc.to_dict()

        _meta = api_doc.get('_meta', {})

        res = get_api_metadata_by_url(_meta['url'])

        if res['metadata'] and isinstance(res['metadata'], dict):
            _meta['timestamp'] = dt.now().isoformat()
            res['metadata']['_meta'] = _meta
            # self._doc.update(id=_id, refresh=True, _meta=res['metadata']['_meta'])
            self._doc.update(id=_id, refresh=True, **res['metadata'])
            return {'updated': f"API with ID {_id} was refreshed"}
        else:
            return {'because': 'Invalid input data.'}

    def delete_slug(self, _id, user, slug_name):
        """
        delete the slug of API _id.
        used in APIMetaDataHandler [DELETE]

        Args:
            _id (str): ID of doc
            user (dict): user info of requester
            slug_name (str): slug name registered
        """
        if not API_Doc.exists(_id):
            return {"because": "Could not retrieve API '{}' to delete slug name".format(_id)}

        i = API_Doc.get(id=_id).to_dict()
        _user = i.get('_meta', {}).get('github_username', '')

        # Make sure this is the correct user
        if user.get('login', None) != _user:
            return {"because": "User '{}' is not the owner of API '{}'".format(user.get('login', None), _id)}

        # Make sure this is the correct slug name
        if self._doc.to_dict().get('_meta', {}).get('slug', '') != slug_name:
            return {"because": "API '{}' slug name is not '{}'".format(_id, slug_name)}

        self._doc.update(id=_id, refresh=True, _meta={"slug": ""})

        return {"{}".format(_id): "slug '{}' deleted".format(slug_name)}
