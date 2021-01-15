"""
Controllers for API doc addition
and API metadata operations
"""
import copy
import gzip
import json
import logging
import string
from abc import ABC, abstractmethod
from collections import OrderedDict
from datetime import datetime as dt

from jsonschema import ValidationError, validate

from model import APIDoc
from utils.downloader import DownloadError, SchemaDownloader

logger = logging.getLogger(__name__)

# *****************************************************************************
# Validation schemas, tags
# *****************************************************************************

# V2 Schemas
SWAGGER2_SCHEMA_URL = 'https://raw.githubusercontent.com/swagger-api/swagger-editor/v3.6.1/src/plugins/validate-json-schema/structural-validation/swagger2-schema.js'

# V3 Schemas
TRANSLATOR_URL = 'https://raw.githubusercontent.com/NCATSTranslator/translator_extensions/main/x-translator/smartapi_x-translator_schema.json'
OAS3_SCHEMA_URL = 'https://raw.githubusercontent.com/swagger-api/swagger-editor/v3.7.1/src/plugins/json-schema-validator/oas3-schema.yaml'

# List of root keys that should be indexed in version 2 schema
SWAGGER2_INDEXED_ITEMS = ['info', 'tags', 'swagger', 'host', 'basePath']

# list of major versions of schema that we support
SUPPORTED_SCHEMA_VERSIONS = ['SWAGGER2', 'OAS3']

downloader = SchemaDownloader()

try:
    downloader.register('swagger_v2', SWAGGER2_SCHEMA_URL)
    downloader.register('openapi_v3', OAS3_SCHEMA_URL)
    downloader.register('x-translator', TRANSLATOR_URL)
except DownloadError:
    pass

# *****************************************************************************
# Custom Exceptions
# *****************************************************************************

class RegistryError(Exception):
    """General API error"""

# *****************************************************************************
# API Doc Controller
# *****************************************************************************

class SmartAPI(ABC):

    def __init__(self, metadata):
        self._metadata = metadata
        self.url = ''
        self.username = ''
        self.slug = ''
        self.etag = ''
        self._meta = {
            "github_username": self.username,
            'url': self.url,
            'timestamp': dt.now().isoformat(),
            'ETag': self.etag
        }
        self.id = ''
        self._es_doc = None

    def __getitem__(self, key):
        return self._metadata[key]

    @property
    @abstractmethod
    def version(self):
        pass

    @staticmethod
    def exists(_id):
        return APIDoc.exists(_id)

    @abstractmethod
    def validate(self):
        pass

    # POST
    @abstractmethod
    def save(self):
        pass

    @staticmethod
    def from_dict(dic):
        if 'openapi' in dic:
            return V3Metadata(dic)
        elif 'swagger' in dic:
            return V2Metadata(dic)
        else:
            raise RegistryError('Version unknown')

    @classmethod
    def validate_slug_name(cls, slug_name):
        """
        Function that determines whether slug_name is a valid slug name
        """
        _valid_chars = string.ascii_letters + string.digits + "-_~"
        _slug = slug_name.lower()
        if _slug in ('www', 'dev', 'smart-api'):
            raise RegistryError(f"Slug name {slug_name} is reserved, please choose another")
        if not all([x in _valid_chars for x in _slug]):
            raise RegistryError(f"Slug name {slug_name} contains invalid characters")
        if APIDoc.exists(_slug, field="._meta.slug"):
            raise RegistryError(f"Slug name {slug_name} already exists")

    # GET
    @classmethod
    def get_api_by_id(cls, _id):
        """
        Get one doc by id
        """
        doc = APIDoc.get(_id)

        _raw = gzip.decompress(base64.urlsafe_b64decode(doc['~raw'])).decode('utf-8')
        d = json.loads(_raw)
        d2 = OrderedDict()
        for key in ['openapi', 'info', 'servers', 'externalDocs', 'tags', 'security', 'paths', 'components']:
            if key in d:
                d2[key] = d[key]
        for key in d:
            if key not in d2:
                d2[key] = d[key]

        cls.id = doc.meta.id
        cls.slug = doc.to_dict().get('_meta', {}).get('slug', '')
        cls.url = doc.to_dict().get('_meta', {}).get('url', '')
        cls.etag = doc.to_dict().get('_meta', {}).get('ETag', '')
        cls.username = doc.to_dict().get('_meta', {}).get('github_username', '')
        cls._es_doc = doc

        return cls.from_dict(d2)

    @classmethod
    def get_api_by_slug(cls, slug):
        """
        Get one doc by slug
        """
        search = APIDoc.search().filter('term', _meta__slug=slug)
        assert search.count() == 1

        doc = next(iter(search)).to_dict(include_meta=True)
        doc.update(doc.pop('_source'))
        doc.pop('_index')

        cls.id = doc.meta.id
        cls.slug = doc.to_dict().get('_meta', {}).get('slug', '')
        cls.url = doc.to_dict().get('_meta', {}).get('url', '')
        cls.etag = doc.to_dict().get('_meta', {}).get('ETag', '')
        cls.username = doc.to_dict().get('_meta', {}).get('github_username', '')
        cls._es_doc = doc

        return cls.from_dict(doc)

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

    # PUT
    def update_slug(self):
        """
        Update API doc registered slug name
        """
        self.validate_slug_name(self.slug)

        self._es_doc.update(_meta={"slug": self.slug.lower()})
        return self.slug.lower()

    def refresh(self):
        """
        refresh the given API document object based on its saved metadata url
        """
        api_doc = self._es_doc

        file = SchemaDownloader.download(self.url)
        res = file.data
        self._meta['ETag'] = file.etag
        res['_meta'] = self._meta

        return api_doc.update(** res)

    # DELETE
    def delete(self):
        """
        delete api
        """
        self._es_doc.delete()
        return self.id

class V3Metadata(SmartAPI):

    def __init__(self, metadata):
        """
        OAS3 V3 Metadata
        """
        super().__init__(metadata)
        assert metadata['openapi'].split('.')[0] == "3"

    @property
    def version(self):
        return 'v3'

    def validate(self):

        for name, schema in downloader.schemas.items():
            if name in ['openapi_v3', 'x-translator']:
                try:
                    validate(instance=self._metadata, schema=schema)
                except ValidationError as e:
                    err_msg = f"Validation Error [{name}]: {e.message}. In: {e.path}"
                    raise RegistryError(err_msg)
                except Exception as e:
                    err_msg = f"Unexpected Validation Error [{name}]: {type(e).__name__} - {e}"
                    raise RegistryError(err_msg)

    def save(self):
        """
        Save an OpenAPI V3 document

        Returns saved API ID
        """

        self.validate()

        # transform paths
        data = copy.copy(self._metadata)
        data['_meta'] = self._meta

        # convert paths to a list of each path item
        paths = []
        for path in data.get('paths', []):
            paths.append({
                "path": path,
                "pathitem": data['paths'][path]
            })
        if paths:
            data['paths'] = paths

        self._es_doc = APIDoc(**data)
        self._es_doc.save()
        return self._es_doc.meta.id

class V2Metadata(SmartAPI):

    def __init__(self, metadata):
        """
        Swagger V2 Metadata
        """
        super().__init__(metadata)
        assert metadata['swagger'].split('.')[0] == "2"

    @property
    def version(self):
        return 'v2'

    def validate(self):

        for name, schema in downloader.schemas.items():
            if name in ['swagger_v2']:
                try:
                    validate(instance=self._metadata, schema=schema)
                except ValidationError as e:
                    err_msg = f"Validation Error [{name}]: {e.message}. In: {e.path}"
                    raise RegistryError(err_msg)
                except Exception as e:
                    err_msg = f"Unexpected Validation Error [{name}]: {type(e).__name__} - {e}"
                    raise RegistryError(err_msg)

    def save(self):
        """
        Save a Swagger V2 document

        Returns saved API ID
        """
        self.validate()

        # transform paths
        data = {"_meta": self._meta}
        for key in SWAGGER2_INDEXED_ITEMS:
            if key in self._metadata:
                data[key] = self._metadata[key]

        self._es_doc = APIDoc(**data)
        self._es_doc.save()

        return self._es_doc.meta.id
