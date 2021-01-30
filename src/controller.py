"""
Controllers for API doc addition
and API metadata operations
"""
import base64
import copy
import gzip
import inspect
import json
import logging
import string
import sys
from abc import ABC, abstractmethod
from collections import OrderedDict, UserDict, UserString
from collections.abc import Iterable, Mapping
from configparser import ConfigParser
from datetime import datetime
from email.utils import parsedate_to_datetime
from types import MappingProxyType
from urllib.parse import scheme_chars, urlparse

import elasticsearch
import jsonschema
import requests
from elasticsearch.exceptions import NotFoundError as ESNotFoundError

from model import APIDoc, APIMeta
from utils import decoder, monitor
from utils.downloader import Downloader, DownloadError, File, download

if sys.version_info.major >= 3 and sys.version_info.minor >= 6:
    from hashlib import blake2b
else:
    from pyblake2 import blake2b  # pylint: disable=import-error

logger = logging.getLogger(__name__)

config = ConfigParser()
config.read('schemas.ini')

# NOTE
# Consider allowing the application to launch
# when the core schema download fails. If that
# happens, disable any modifications and alert
# some slack channel to report the event.

openapis = Downloader()
openapis.download(
    config['openapi'].keys(),
    config['openapi'].values()
)
swaggers = Downloader()
swaggers.download(
    config['swagger'].keys(),
    config['swagger'].values()
)


class ControllerError(Exception):
    pass


class NotFoundError(ControllerError):
    pass


class ConflictError(ControllerError):
    pass

# TODO username migration
# TODO change asserts to ifs
# TODO multiple time validation


def validate(doc, schemas):
    """
        Validate a document agasint schemas.
        Schemas is a dict of name and schema pairs.
    """

    # required by jsonschema package
    if not isinstance(doc, dict):
        doc = decoder.to_dict(doc)

    try:  # validate agasint every schema
        for name, schema in schemas.items():
            jsonschema.validate(doc, schema)

    except jsonschema.ValidationError as err:
        _ = (
            f"Failed {name} validation at"
            f"{err.path} - {err.message}. "
            # show path first, message can
            # sometimes be very very long
        )
        raise ValueError(_) from err

    except Exception as err:
        _ = (
            f"Unexpected Validation Error: "
            f"{type(err).__name__} - {err}"
        )
        raise ValueError(_) from err


class Format(UserDict):

    KEYS = ()
    SCHEMAS = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = OrderedDict(self.data)
        self.order()

    def order(self):
        for key in reversed(self.KEYS):
            if key in self.data:  # important
                self.data.move_to_end(key, False)

    def validate(self):
        validate(self.data, self.SCHEMAS)

    def clean(self):
        self.data = OrderedDict({
            k: v for k, v in self.data.items()
            if k in self.KEYS
        })


class OpenAPI(Format):

    KEYS = (
        'openapi', 'info', 'servers',
        'externalDocs', 'tags', 'security',
        'paths', 'components'
    )
    SCHEMAS = openapis

    def clean(self):
        super().clean()
        if isinstance(self.data.get('paths'), dict):
            self.data['paths'] = [
                {
                    "path": key,
                    "pathitem": val
                }
                for key, val in self.data['paths'].items()
            ]


class Swagger(Format):

    KEYS = (
        'info', 'tags', 'swagger',
        'host', 'basePath'
    )
    SCHEMAS = swaggers


class PlaceHolder(UserString):
    pass


class AbstractWebEntity(ABC):
    """
        A web entity identified by a URL.
        It corresponds to a database entry.
        The primary key is the hash of the URL.
    """

    def __init__(self, url):

        assert isinstance(url, (str, PlaceHolder)) and url
        assert urlparse(str(url)).scheme in ('http', 'https')

        self._url = url

    @property
    def _id(self):
        # can be a cached property in python 3.8+
        _bytes = str(self._url).encode('utf8')
        _hash = blake2b(_bytes, digest_size=16)
        return _hash.hexdigest()

    @property
    def url(self):
        """
        The URL of this API specification document.
        This field is read-only and generates the _id.
        """
        # why read-only?
        # since url is linked to the _id
        # it's not trivial to handle url change in DB
        return self._url

    @classmethod
    @abstractmethod
    def get(cls, _id):
        """
        Retrieve the existing record in database.
        """

    @abstractmethod
    def save(self):
        """
        Save or update this entity in database.
        May perform partial updates behind the scene.
        """

    @abstractmethod
    def delete(self):
        """
        Delete this entity in database.
        May also delete associated entities.
        """


class AbstractStatus(AbstractWebEntity):
    """
        The point-in-time status of a web entity.
        And the timestamp associated with the status.
    """

    def __init__(self, url, ts=None):
        super().__init__(url)

        self.status = None
        self._timestamp = ts

    @property
    def timestamp(self):
        """
        Timestamp at which the "status" recorded is achieved.
        Correspond to a refresh event. Cannot change directly.
        """
        return self._timestamp

    @abstractmethod
    def save(self):

        try:  # partial update
            doc = APIMeta.get(self._id)
        except ESNotFoundError:
            doc = APIMeta()  # new record
            doc.meta.id = self._id
            doc.url = self.url

        return doc

        # more class specific logic is
        # to be implemented in sub-classes

    def delete(self):

        # need to delete through primary object
        # use SmartAPI class to perform deletion.
        raise ControllerError("Not allowed.")

    @abstractmethod
    def refresh(self, content=None):
        """
        Refresh the status of this web entity.
        Optionally with the content provided as parameter.
        Update the timestamp to reflect the operation.
        The timestamp can be server or local time.
        """

    def refresh_timestamp(self):
        """
        Update the timestamp to the current time.
        Used for manual update of fields.
        """
        self._timestamp = datetime.utcnow()


class AbstractDoc(AbstractWebEntity, Mapping):
    """
        A mapping defined by JSON/YAML encoded bytes.
        The object level shallow access is read-only.
    """

    def __init__(self, url):
        super().__init__(url)

        self._raw = None
        self._data = {}

    @property
    def raw(self):
        """
        Bytes that correspond to the URL.
        This object is a view of this field.
        """
        return self._raw

    @raw.setter
    def raw(self, value):

        if value is None:
            self._raw = None
            return  # allow None

        try:
            self._data = decoder.to_dict(value)
        except (ValueError, TypeError) as err:
            raise ControllerError(str(err)) from err
        else:  # dict conversion success
            self._raw = value

    def __getitem__(self, key):
        return self._data.__getitem__(key)

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)


class APIMonStat(AbstractStatus):

    @classmethod
    def get(cls, _id):

        try:
            meta = APIMeta.get(_id)
        except ESNotFoundError as err:
            raise NotFoundError from err

        doc = cls(meta.url, meta.uptime_ts)
        doc.status = meta.uptime_status

        return doc

    def refresh(self, content=None):

        if content:
            self.status = content
        else:
            doc = SmartAPI.get(self._id)
            api = monitor.API(doc)
            api.check_api_status()  # blocking
            self.status = api.api_status

        self.refresh_timestamp()

    def save(self):

        meta = super().save()
        meta.uptime_status = self.status
        meta.uptime_ts = self.timestamp
        meta.save()

        return self._id


class APIWebDoc(AbstractStatus, AbstractDoc):

    def __init__(self, url, ts=None):
        super().__init__(url, ts)

        self.raw = None
        self.etag = None

    @classmethod
    def get(cls, _id):

        try:
            meta = APIMeta.get(_id)
        except ESNotFoundError as err:
            raise NotFoundError from err

        doc = cls(meta.url, meta.web_ts)
        doc.raw = decoder.decompress(meta.web_raw)
        doc.etag = meta.web_etag
        doc.status = meta.web_status

        return doc

    def refresh(self, content=None):

        if isinstance(content, File):
            file = content
        else:  # blocking network operation
            file = download(self.url)

        self.raw = file.raw
        self.etag = file.etag
        self.status = file.status
        self._timestamp = file.date

        if not self._timestamp:
            self.refresh_timestamp()

    def save(self):

        meta = super().save()
        meta.meta.id = self._id
        meta.web_status = self.status
        meta.web_etag = self.etag
        meta.web_raw = decoder.compress(self.raw)
        meta.web_ts = self.timestamp
        meta.save()

        return self._id


class Slug():
    """
        Optional secondary key for a DB entry.
        It must be a unique string or None.
    """

    def __get__(self, obj, objtype=None):
        if obj is None:  # class atrribute
            return self
        return getattr(obj, '_slug', None)

    def __set__(self, obj, value):
        self.validate(value)
        setattr(obj, '_slug', value)

    def validate(self, value):

        if value is None:
            return  # this field is optional, okay to be None

        if not isinstance(value, str) or len(value) < 3:
            raise ValueError("Slug must be at least 3 characters.")

        if value != value.lower():
            raise ValueError("Slug must be in lowercase.")

        if value in ('www', 'dev', 'smart-api', 'api'):
            raise ValueError(f"Slug '{value}' is reserved.")

        _valid_chars = string.ascii_letters + string.digits + "-_~"
        if not all(c in _valid_chars for c in value):
            raise ValueError("Slug contains invalid characters.")


class SmartAPI(AbstractDoc):

    # SmartAPI.slug.validate(value: Union[str, NoneType]) -> None
    # smartapi.slug : Union[str, NoneType]
    slug = Slug()

    # use this as url for validation only workflow
    VALIDATION_ONLY = PlaceHolder("http://localhost/doc")

    def __init__(self, url, raw):

        super().__init__(url)

        self.username = None
        self.slug = None
        self.raw = raw

    @property
    def version(self):
        """
        API specification format version name.
        This field decides how it is saved in ES.
        """
        if 'openapi' in self._data:
            return 'openapi'
        if 'swagger' in self._data:
            return 'swagger'
        return None

    @classmethod
    def exists(cls, _id):
        """
        If a SmartAPI document exists in database.
        Do NOT fully rely on this for other operations.
        """
        # Data can change in between calls.
        # Use try-catch blocks in follow up ops.

        return bool(APIDoc.exists(_id))

    @classmethod
    def find(cls, val, field='slug'):
        """
        Find a SmartAPI by a field other than _id.
        Return the first _id or None if no match.
        """
        # Data can change in between calls.
        # Use try-catch blocks in follow up ops.

        if field in ('slug', 'username', 'url'):
            field = '_meta.' + field

        return APIDoc.exists(val, field)

    @classmethod
    def get(cls, _id):

        try:
            doc = APIDoc.get(_id)
        except ESNotFoundError as err:
            raise NotFoundError from err

        raw = decoder.decompress(doc._raw)

        obj = cls(doc._meta.url, raw)
        obj.username = doc._meta.username
        obj.slug = doc._meta.slug

        return obj

    def validate(self):
        """
        Validate the properties and the mapping document.
        Return a formatted object basing on format version.
        Raise exceptions on all types of errors anywhere.
        """

        if not self.version:
            raise ControllerError("Unknown version.")

        if self.version == 'openapi':
            doc = OpenAPI(self._data)
        else:  # then it must be swagger
            doc = Swagger(self._data)

        try:
            doc.validate()  # basing on its format
        except ValueError as err:
            raise ControllerError(str(err)) from err

        return doc

    def save(self):

        if not self.username:
            raise ControllerError("Username is required.")

        if self.url is self.VALIDATION_ONLY:
            raise ControllerError("In validation-only mode.")

        _doc = self.validate()
        _doc.clean()  # only keep indexing fields

        if self.slug:
            _id = self.find(self.slug)
            if _id and _id != self._id:  # another doc same slug.
                raise ConflictError("Slug is already registered.")

        # NOTE
        # if the slug of another document changed at this point
        # it's possible to have two documents with the same slug
        # registered. but it should be rare enough in reality.

        doc = APIDoc(**_doc)
        doc.meta.id = self._id
        doc._meta.url = self.url
        doc._meta.timestamp = datetime.utcnow()
        doc._meta.username = self.username
        doc._meta.slug = self.slug
        doc._raw = decoder.compress(self.raw)
        doc.save()

        return self._id

    @classmethod
    def get_all(cls, size=10, from_=0):
        """
        Returns a list of SmartAPIs.
        Size is the at-most number.
        """
        search = APIDoc.search()
        search = search.source(False)
        search = search[from_: from_ + size]

        for hit in search:
            try:  # unlikely but possible
                doc = cls.get(hit.meta.id)
            except ESNotFoundError:
                pass  # inconsistent
            else:  # consistent
                yield doc

    @staticmethod
    def get_tags(field='info.contact.name'):
        """
        Perform aggregations on a given field.
        For example: generate list of tags and authors.

        Result looks like:
        {
            "tagC" : 60,
            "tagA" : 10,
            "tagB" : 2,
            ...
        }
        """
        return APIDoc.aggregate(field)

    def delete(self):

        try:  # primary index
            APIDoc.get(self._id).delete()
        except ESNotFoundError as err:
            raise NotFoundError() from err

        try:  # secondary index
            APIMeta.get(self._id).delete()
        except ESNotFoundError:
            pass

        return self._id
