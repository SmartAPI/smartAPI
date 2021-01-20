"""
Controllers for API doc addition
and API metadata operations
"""
import copy
import gzip
import base64
import json
import logging
import string
from abc import ABC, abstractmethod
from collections import OrderedDict, UserDict
from datetime import datetime as dt

from jsonschema import ValidationError, validate

from model import APIDoc
from utils.downloader import DownloadError, SchemaDownloader

logger = logging.getLogger(__name__)

# *****************************************************************************
# Validation schemas, tags
# *****************************************************************************

# V2 Schemas
SWAGGER2_SCHEMA_URL = 'https://raw.githubusercontent.com/swagger-api/swagger-editor/'\
    'v3.6.1/src/plugins/validate-json-schema/structural-validation/swagger2-schema.js'
# V3 Schemas
TRANSLATOR_URL = 'https://raw.githubusercontent.com/NCATSTranslator/'\
    'translator_extensions/main/x-translator/smartapi_x-translator_schema.json'
OAS3_SCHEMA_URL = 'https://raw.githubusercontent.com/swagger-api/'\
    'swagger-editor/v3.7.1/src/plugins/json-schema-validator/oas3-schema.yaml'

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

class SmartAPI(UserDict, ABC):
    """
    Create a SmartAPI object from
    openapi v3 or swagger v2 metadata
    eg. SmartAPI.from_dict(data)
    """

    def __init__(self, metadata):
        super().__init__(metadata)
        self._metadata = self.data
        self.url = ''
        self.username = ''
        self.slug = ''
        self.etag = ''
        self.id = ''  # pylint: disable=invalid-name 
        self._es_doc = None

    @property
    @abstractmethod
    def version(self):
        pass

    @classmethod
    def exists(cls, _id, field="_id"):
        _id = APIDoc.exists(_id, field)
        if _id:
            return cls.get_api_by_id(_id)
        return None

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
        data = json.loads(_raw)
        # return main keys back in preferred order
        doc_2 = OrderedDict()
        for key in ['openapi', 'info', 'servers',
                    'externalDocs', 'tags', 'security', 'paths', 'components']:
            if key in data:
                doc_2[key] = data[key]
        for key in data:
            if key not in doc_2:
                doc_2[key] = data[key]

        obj = cls.from_dict(doc_2)

        obj._es_doc = doc
        obj.id = doc.meta.id
        obj.username = doc._meta.github_username  # pylint: disable=protected-access
        obj.slug = doc._meta.slug  # pylint: disable=protected-access
        obj.url = doc._meta.url  # pylint: disable=protected-access
        obj.etag = doc._meta.etag  # pylint: disable=protected-access
        return obj

    @classmethod
    def get_api_by_slug(cls, slug):
        """
        Get one doc by slug
        """
        if not APIDoc.exists(slug, "._meta.slug"):
            raise RegistryError(f'slug [{slug}] does not exist')

        search = APIDoc.search().filter('term', _meta__slug=slug)
        assert search.count() == 1

        doc = next(iter(search)).to_dict(include_meta=True)
        doc.update(doc.pop('_source'))
        doc.pop('_index')

        obj = cls.from_dict(doc)

        obj._es_doc = doc
        obj.id = doc.meta.id
        obj.username = doc._meta.github_username  # pylint: disable=protected-access
        obj.slug = doc._meta.slug  # pylint: disable=protected-access
        obj.url = doc._meta.url  # pylint: disable=protected-access
        obj.etag = doc._meta.etag  # pylint: disable=protected-access

        return obj

    @staticmethod
    def get_all(fields=(), from_=0, size=10):
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
        file = SchemaDownloader.download(self.url)
        self._metadata = file.data
        self.etag = file.etag
        self.save()
        return self.etag

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
            if name != "swagger_v2":
                try:
                    validate(instance=self._metadata, schema=schema)
                except ValidationError as err:
                    err_msg = f"Validation Error [{name}]: {err.message}. In: {err.path}"
                    raise RegistryError(err_msg) from err
                except Exception as err:
                    err_msg = f"Unexpected Validation Error [{name}]: {type(err).__name__} - {err}"
                    raise RegistryError(err_msg) from err

    def save(self):
        """
        Save an OpenAPI V3 document

        Returns saved API ID
        """
        self.validate()

        # transform paths
        data = copy.copy(self._metadata)
        paths = []
        for path in data.get('paths', []):
            paths.append({
                "path": path,
                "pathitem": data['paths'][path]
            })
        if paths:
            data['paths'] = paths

        _raw = json.dumps(self._metadata).encode('utf-8')
        _raw = base64.urlsafe_b64encode(gzip.compress(_raw)).decode('utf-8')
        data["~raw"] = _raw

        self._es_doc = APIDoc(**data)
        self._es_doc._meta.Etag = self.etag
        self._es_doc._meta.url = self.url
        self._es_doc._meta.github_username = self.username
        self._es_doc._meta.slug = self.slug
        self._es_doc._meta.timestamp = dt.now().isoformat()

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
        if 'swagger_v2' in downloader.schemas:
            try:
                validate(instance=self._metadata, schema=downloader.schemas['swagger_v2'])
            except ValidationError as err:
                err_msg = f"Validation Error [Swagger_V2]: {err.message}. In: {err.path}"
                raise RegistryError(err_msg) from err
            except Exception as err:
                err_msg = f"Unexpected Validation Error [Swagger_V2]: {type(err).__name__} - {err}"
                raise RegistryError(err_msg) from err

    def save(self):
        """
        Save a Swagger V2 document

        Returns saved API ID
        """
        self.validate()

        data = {}
        for key in SWAGGER2_INDEXED_ITEMS:
            if key in self._metadata:
                data[key] = self._metadata[key]

        _raw = json.dumps(self._metadata).encode('utf-8')
        _raw = base64.urlsafe_b64encode(gzip.compress(_raw)).decode('utf-8')
        data["~raw"] = _raw

        self._es_doc = APIDoc(**data)
        self._es_doc._meta.Etag = self.etag
        self._es_doc._meta.url = self.url
        self._es_doc._meta.github_username = self.username
        self._es_doc._meta.slug = self.slug
        self._es_doc._meta.timestamp = dt.now().isoformat()

        self._es_doc.save()
        return self._es_doc.meta.id
