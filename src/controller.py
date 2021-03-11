"""
    SmartAPI CRUD Validation and Refresh Operations

    Validation only:

        smartapi = SmartAPI(SmartAPI.VALIDATION_ONLY)
        smartapi.raw = rawbytes
        smartapi.validate()

    Add a document:

        smartapi = SmartAPI(url)
        smartapi.raw = rawbytes

        smartapi.username = username
        smartapi.slug = slug # optional

        smartapi.validate() # should be called before saving
        smartapi.save()

        smartapi.check() # populate uptime status
        smartapi.refresh() # refresh and populate refresh status, auto validate
        smartapi.save()

    Modify a document metadata:

        smartapi = SmartAPI.get(_id)
        smartapi.slug = newslug
        smartapi.save()

    Delete a document:

        smartapi = SmartAPI.get(_id)
        smartapi.delete()

"""
import logging
import string
import sys
from abc import ABC, abstractmethod
from collections import OrderedDict, UserDict, UserString
from collections.abc import Mapping
from configparser import ConfigParser
from datetime import datetime, timezone
from enum import IntEnum
from urllib.parse import urlparse
from warnings import warn

import jsonschema
from elasticsearch.exceptions import NotFoundError as ESNotFoundError

from model import APIDoc
from utils import decoder, monitor
from utils.downloader import Downloader, File, download

if sys.version_info.major >= 3 and sys.version_info.minor >= 6:
    from hashlib import blake2b
else:
    from pyblake2 import blake2b  # pylint: disable=import-error

logger = logging.getLogger(__name__)

config = ConfigParser()
config.read('schemas.ini')

# TODO etag support

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
            f"Failed {name} validation at "
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

    def transform(self):
        if isinstance(self.data.get('paths'), dict):
            self.data['paths'] = [
                {
                    "path": key,
                    "pathitem": val
                }
                for key, val in self.data['paths'].items()
            ]

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


class AbstractEntityStatus():
    """
        With a point-in-time status of a web entity.
        And the timestamp associated with the status.
    """
    # Corresponds to a group of _status fields in SmartAPI.

    def __init__(self, entity, status=None, timestamp=None):

        self._entity = entity
        self._status = status
        self._timestamp = timestamp

    @property
    def timestamp(self):
        """
        Timestamp at which the "status" recorded is achieved.
        Correspond to a refresh event. Cannot change directly.
        """
        return self._timestamp

    @property
    def status(self):
        """
        The position of affairs at the particular time recorded
        by its timestamp attribute. Modifiable through update.
        Update of this field also updates the timestamp field.
        """
        return self._status

    @abstractmethod
    def update(self, content):
        """
        Update the status of this web entity with the content provided.
        The content should indicate a certain type of status.
        Update the timestamp to reflect the operation.
        The timestamp can be server or local time.
        """
        self._timestamp = datetime.utcnow()
        self._timestamp.replace(tzinfo=timezone.utc)


class APIMonitorStatus(AbstractEntityStatus):
    """
        API Uptime Monitor Status.
        See utils.monitor for details.
    """

    def update(self, content):
        super().update(content)
        self._status = content


class APIRefreshStatus(AbstractEntityStatus):
    """
        API Document Refresh Status.
        Support HTTP status codes and the ones below.
    """

    class STATUS(IntEnum):
        """ Code Expansion """
        NOT_MODIFIED = 200  # no need to update, already at latest version
        UPDATED = 299  # new version available and update successful
        INVALID = 499  # cannot update to new version because validation failed

    def update(self, content):

        if not isinstance(content, File):
            raise TypeError("Invalid content.")

        super().update(content)
        self._status = content.status

        if content.date:  # more accurate
            self._timestamp = content.date

        if content.status != 200 or not content.raw:
            return  # no need to update _raw

        try:
            smartapi = SmartAPI(SmartAPI.VALIDATION_ONLY)
            smartapi.raw = content.raw
            smartapi.validate()
        except ControllerError:
            self._status = self.STATUS.INVALID.value
        else:  # safe to update
            if self._entity.raw in (content.raw, None):
                self._status = self.STATUS.NOT_MODIFIED.value
            else:  # raw field changed
                self._status = self.STATUS.UPDATED.value
            self._entity.raw = content.raw


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


class SmartAPI(AbstractWebEntity, Mapping):

    # SmartAPI.slug.validate(value: Union[str, NoneType]) -> None
    # smartapi.slug : Union[str, NoneType]
    slug = Slug()

    # use this as url for validation only workflow
    VALIDATION_ONLY = PlaceHolder("http://nohost/nofile")

    def __init__(self, url):

        super().__init__(url)

        self.uptime = APIMonitorStatus(self)
        self.webdoc = APIRefreshStatus(self)

        self.username = None
        self.slug = None

        self.date_created = None
        self.last_updated = None

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

        if not value:
            raise ControllerError("Empty value.")
        try:
            self._data = decoder.to_dict(value)
        except (ValueError, TypeError) as err:
            raise ControllerError(str(err)) from err
        else:  # dict conversion success
            self._raw = value

        # update the timestamps
        self.last_updated = datetime.now(timezone.utc)
        if not self.date_created:
            self.date_created = self.last_updated

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

        obj = cls(doc._meta.url)
        obj.raw = decoder.decompress(doc._raw)

        obj.username = doc._meta.username
        obj.slug = doc._meta.slug

        obj.date_created = doc._meta.date_created
        obj.last_updated = doc._meta.last_updated

        obj.uptime = APIMonitorStatus(
            obj, doc._status.uptime_status,
            doc._status.uptime_ts
        )

        obj.webdoc = APIRefreshStatus(
            obj, doc._status.refresh_status,
            doc._status.refresh_ts
        )

        return obj

    def _validate_dispatch(self):

        if not self.version:
            raise ControllerError("Unknown version.")

        if self.version == 'openapi':
            doc = OpenAPI(self._data)
        else:  # then it must be swagger
            doc = Swagger(self._data)

        return doc

    def validate(self):
        """
        Validate the properties and the mapping document.
        Return a formatted object basing on format version.
        Raise exceptions on all types of errors anywhere.
        """

        doc = self._validate_dispatch()
        try:
            doc.validate()  # basing on its format
        except ValueError as err:
            raise ControllerError(str(err)) from err

        return doc

    def check(self):

        doc = dict(self)
        doc['_id'] = self._id

        api = monitor.API(doc)
        api.check_api_status()  # blocking network operation

        self.uptime.update(api.api_status)
        return api.api_status

    def refresh(self, file=None):

        if file is None:  # blocking network operation
            file = download(self.url, raise_error=False)

        self.webdoc.update(file)
        return self.webdoc.status

    def save(self):
        # TODO DOCSTRING

        if not self.raw:
            raise ControllerError("No content.")

        if not self.username:
            raise ControllerError("Username is required.")

        if self.url is self.VALIDATION_ONLY:
            raise ControllerError("In validation-only mode.")

        if not self.last_updated:
            self.last_updated = datetime.now(timezone.utc)
            warn("Filling in date_updated with current time.")
        if not self.date_created:
            self.date_created = self.last_updated
            warn("Filling in date_created with current time.")

        if not isinstance(self.date_created, datetime):
            raise ControllerError("Invalid created time.")
        if not isinstance(self.last_updated, datetime):
            raise ControllerError("Invalid updated time.")
        if self.date_created > self.last_updated:
            raise ControllerError("Invalid timestamps.")

        # NOTE
        # why not enforce validation here?
        # we add additional constraints to the application from time to time
        # it's actually hard to retrospectively make sure all previously
        # submitted API document always meet our latest requirements

        _doc = self._validate_dispatch()
        _doc.transform()

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
        doc._meta.username = self.username
        doc._meta.slug = self.slug

        doc._meta.date_created = self.date_created
        doc._meta.last_updated = self.last_updated

        doc._status.uptime_status = self.uptime.status
        doc._status.uptime_ts = self.uptime.timestamp

        doc._status.refresh_status = self.webdoc.status
        doc._status.refresh_ts = self.webdoc.timestamp

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

        try:
            APIDoc.get(self._id).delete()
        except ESNotFoundError as err:
            raise NotFoundError() from err

        return self._id

    # READ-ONLY DICT-LIKE ACCESS
    # FOR FIRST LEVEL KEYS

    def __getitem__(self, key):
        return self._data.__getitem__(key)

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)
