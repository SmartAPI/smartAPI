from abc import ABC, abstractmethod
from collections import OrderedDict, UserDict, UserString
from datetime import datetime, timezone
from enum import IntEnum
from hashlib import blake2b  # requires python>=3.6, otherwise install pyblake2
from urllib.parse import urlparse
import jsonschema
from configparser import ConfigParser
from elasticsearch.exceptions import NotFoundError as ESNotFoundError

from utils import decoder, monitor
from utils.downloader import download, Downloader, File
from .exceptions import ControllerError, NotFoundError

# NOTE
# Consider allowing the application to launch
# when the core schema download fails. If that
# happens, disable any modifications and alert
# some slack channel to report the event.

config = ConfigParser()
config.read("schemas.ini")

openapis = Downloader()
openapis.download(config["openapi"].keys(), config["openapi"].values())

swaggers = Downloader()
swaggers.download(config["swagger"].keys(), config["swagger"].values())


def validate(doc, schemas):
    """
    Validate a document agasint schemas.
    Schemas is a dict of name and schema pairs.
    """

    # required by jsonschema package
    if not isinstance(doc, dict):
        doc = decoder.to_dict(doc)

    try:  # validate agasint every schema
        for _name, schema in schemas.items():
            jsonschema.validate(doc, schema)

    except jsonschema.ValidationError as err:
        _ = (
            f"Failed {_name} validation at "
            f"{err.path} - {err.message}. "
            # show path first, message can
            # sometimes be very very long
        )
        raise ValueError(_) from err

    except Exception as err:
        _ = f"Unexpected Validation Error: " f"{type(err).__name__} - {err}"
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
        if isinstance(self.data.get("paths"), dict):
            self.data["paths"] = [{"path": key, "pathitem": val} for key, val in self.data["paths"].items()]

        # normalize info.x-trapi.test_data_location string value as info.x-trapi.test_data_location.default.url value
        if isinstance(self.data.get("info", {}).get("x-trapi", {}).get("test_data_location"), str):
            self.data["info"]["x-trapi"]["test_data_location"] = {"default": {"url": self.data["info"]["x-trapi"]["test_data_location"]}}

    def clean(self):
        self.data = OrderedDict({k: v for k, v in self.data.items() if k in self.KEYS})


class OpenAPI(Format):

    KEYS = ("openapi", "info", "servers", "externalDocs", "tags", "security", "paths", "components")
    SCHEMAS = openapis


class Swagger(Format):

    KEYS = ("info", "tags", "swagger", "host", "basePath")
    SCHEMAS = swaggers


class PlaceHolder(UserString):
    pass


class AbstractWebEntity(ABC):
    """
    A web entity identified by a URL.
    It corresponds to a database entry.
    The primary key is the hash of the URL.
    """

    LOOKUP_FIELDS = []
    MODEL_CLASS = None

    # use this as url for validation only workflow
    VALIDATION_ONLY = PlaceHolder("http://nohost/nofile")

    def __init__(self, url):

        assert isinstance(url, (str, PlaceHolder)) and url
        assert urlparse(str(url)).scheme in ("http", "https")

        self._url = url

        self.uptime = APIMonitorStatus(self)
        self.webdoc = APIRefreshStatus(self)

        self._raw = None
        self._data = {}

    @staticmethod
    def get_tags(field=None):
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
        raise NotImplementedError()

    @classmethod
    def count(cls, *args, **kwargs):
        search = cls.MODEL_CLASS.search()
        if args or kwargs:
            search = search.filter(*args, **kwargs)
        return search.count()

    @classmethod
    def exists(cls, _id):
        """
        If a SmartAPI document exists in database.
        Do NOT fully rely on this for other operations.
        """
        # Data can change in between calls.
        # Use try-catch blocks in follow up ops.

        return bool(cls.MODEL_CLASS.exists(_id))

    @classmethod
    def find(cls, val, field=None):
        """
        Find an entity by a field other than _id.
        Return the first _id or None if no match.
        """
        # Data can change in between calls.
        # Use try-catch blocks in follow up ops.

        if field in cls.LOOKUP_FIELDS:
            field = "_meta." + field
        return cls.MODEL_CLASS.exists(val, field)

    @classmethod
    def get_all(cls, size=10, from_=0):
        """
        Returns a list of SmartAPIs.
        Size is the at-most number.
        """
        search = cls.MODEL_CLASS.search()
        search = search.source(False)
        search = search[from_: from_ + size]

        for hit in search:
            try:  # unlikely but possible
                doc = cls.get(hit.meta.id)
            except ESNotFoundError:
                pass  # inconsistent
            else:  # consistent
                yield doc

    @classmethod
    def get(cls, _id):
        try:
            doc = cls.MODEL_CLASS.get(_id)
        except ESNotFoundError as err:
            raise NotFoundError from err
        obj = cls(doc.get_url())
        obj._doc = doc
        obj.raw = decoder.decompress(doc._raw)

        obj.uptime = APIMonitorStatus(
            obj,
            (
                doc._status.uptime_status,
                doc._status.uptime_msg,
            ),
            doc._status.uptime_ts,
        )

        obj.webdoc = APIRefreshStatus(
            obj,
            doc._status.refresh_status,
            doc._status.refresh_ts,
        )

        return obj

    @classmethod
    def get_doc_url(cls, doc):
        raise NotImplementedError()

    @property
    def _id(self):
        # can be a cached property in python 3.8+
        _bytes = str(self._url).encode("utf8")
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
        if hasattr(self, 'date_created') and not self.date_created:
            self.date_created = self.last_updated

    def _validate_dispatch(self):
        raise NotImplementedError()

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
        doc["_id"] = self._id

        api = monitor.API(doc)
        api.check_api_status()  # blocking network operation
        status = api.get_api_status()
        self.uptime.update(status)
        return status

    def delete(self):
        try:
            self.MODEL_CLASS.get(self._id).delete()
        except ESNotFoundError as err:
            raise NotFoundError() from err

        return self._id

    def refresh(self, file=None):

        if file is None:  # blocking network operation
            file = download(self.url, raise_error=False)

        self.webdoc.update(file)
        return self.webdoc.status

    def save(self, force_save=True):
        # TODO DOCSTRING

        if not self.raw:
            raise ControllerError("No content.")

        if self.url is self.VALIDATION_ONLY:
            raise ControllerError("In validation-only mode.")

        # NOTE
        # why not enforce validation here?
        # we add additional constraints to the application from time to time
        # it's actually hard to retrospectively make sure all previously
        # submitted API document always meet our latest requirements

        _doc = self._validate_dispatch()
        _doc.transform()

        doc = self.MODEL_CLASS(**_doc)

        if self.uptime.status:
            doc._status.uptime_status = self.uptime.status[0]
            doc._status.uptime_msg = self.uptime.status[1]
        doc._status.uptime_ts = self.uptime.timestamp

        doc._status.refresh_status = self.webdoc.status
        doc._status.refresh_ts = self.webdoc.timestamp

        doc._raw = decoder.compress(self.raw)

        if force_save:
            doc.save(skip_empty=False)

        self._doc = doc
        return self._id

    # READ-ONLY DICT-LIKE ACCESS
    # FOR FIRST LEVEL KEYS

    def __getitem__(self, key):
        return self._data.__getitem__(key)

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)


class AbstractEntityStatus:
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
        """Code Expansion"""

        NOT_MODIFIED = 200  # no need to update, already at latest version
        UPDATED = 299  # new version available and update successful
        INVALID = 499  # cannot update to new version because validation failed

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.APIEntity = self._entity.__class__

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
            entity = self.APIEntity(self.APIEntity.VALIDATION_ONLY)
            entity.raw = content.raw
            entity.validate()
        except ControllerError:
            self._status = self.STATUS.INVALID.value
        else:  # safe to update
            if self._entity.raw in (content.raw, None):
                self._status = self.STATUS.NOT_MODIFIED.value
            else:  # raw field changed
                self._status = self.STATUS.UPDATED.value
            self._entity.raw = content.raw
