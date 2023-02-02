"""
    SmartAPIEntity CRUD Validation and Refresh Operations

    Validation only:

        smartapi = SmartAPIEntity(SmartAPIEntity.VALIDATION_ONLY)
        smartapi.raw = rawbytes
        smartapi.validate()

    Add a document:

        smartapi = SmartAPIEntity(url)
        smartapi.raw = rawbytes

        smartapi.username = username
        smartapi.slug = slug # optional

        smartapi.validate() # should be called before saving
        smartapi.save()

        smartapi.check() # populate uptime status
        smartapi.refresh() # refresh and populate refresh status, auto validate
        smartapi.save()

    Modify a document metadata:

        smartapi = SmartAPIEntity.get(_id)
        smartapi.slug = newslug
        smartapi.save()

    Delete a document:

        smartapi = SmartAPIEntity.get(_id)
        smartapi.delete()

"""
import math
import logging
import string
from collections.abc import Mapping
from datetime import datetime, timezone
from warnings import warn

from model import SmartAPIDoc
from utils import decoder, monitor
from utils.downloader import download
from .metakg import MetaKGEntity
from .base import AbstractWebEntity, OpenAPI, Swagger, APIMonitorStatus, APIRefreshStatus
from .exceptions import ConflictError, ControllerError

logger = logging.getLogger(__name__)

# TODO etag support


class Slug:
    """
    Optional secondary key for a DB entry.
    It must be a unique string or None.
    """

    def __get__(self, obj, objtype=None):
        if obj is None:  # class atrribute
            return self
        return getattr(obj, "_slug", None)

    def __set__(self, obj, value):
        self.validate(value)
        setattr(obj, "_slug", value)

    def validate(self, value):

        if value is None:
            return  # this field is optional, okay to be None

        if not isinstance(value, str) or len(value) < 3:
            raise ValueError("Slug must be at least 3 characters.")

        if value != value.lower():
            raise ValueError("Slug must be in lowercase.")

        if value in ("www", "dev", "smart-api"):
            raise ValueError(f"Slug '{value}' not allowed.")

        _valid_chars = string.ascii_letters + string.digits + "-_"
        if not all(c in _valid_chars for c in value):
            raise ValueError("Slug contains invalid characters.")


class SmartAPIEntity(AbstractWebEntity, Mapping):
    LOOKUP_FIELDS = ("slug", "username", "url")
    MODEL_CLASS = SmartAPIDoc

    # SmartAPIEntity.slug.validate(value: Union[str, NoneType]) -> None
    # smartapi.slug : Union[str, NoneType]
    slug = Slug()

    def __init__(self, url):
        super().__init__(url)
        self.username = None
        self.slug = None
        self.date_created = None
        self.last_updated = None

        self.uptime = APIMonitorStatus(self)
        self.webdoc = APIRefreshStatus(self)

        self._raw = None

    @classmethod
    def get(cls, _id):
        obj = super().get(_id)

        obj.username = obj._doc._meta.username
        obj.slug = obj._doc._meta.slug
        obj.raw = decoder.decompress(obj._doc._raw)

        obj.date_created = obj._doc._meta.date_created
        obj.last_updated = obj._doc._meta.last_updated

        obj.uptime = APIMonitorStatus(
            obj,
            (
                obj._doc._status.uptime_status,
                obj._doc._status.uptime_msg,
            ),
            obj._doc._status.uptime_ts,
        )

        obj.webdoc = APIRefreshStatus(
            obj,
            obj._doc._status.refresh_status,
            obj._doc._status.refresh_ts,
        )
        return obj

    @staticmethod
    def get_tags(field="info.contact.name"):
        return SmartAPIDoc.aggregate(field)

    @classmethod
    def find(cls, val, field="slug"):
        return super().find(val, field=field)

    @classmethod
    def refresh_metakg(cls, include_reasoner=True):
        count_docs = cls.count()
        query_data = {
            'type': 'term',
            'body': {
                'tags.name': 'translator'
            }
        }
        entities = cls.get_all(size=count_docs, query_data=query_data)
        for entity in entities:
            MetaKGEntity.create_by_smartapi(entity, include_reasoner=include_reasoner)

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

    def check(self):

        doc = dict(self)
        doc["_id"] = self._id

        api = monitor.API(doc)
        api.check_api_status()  # blocking network operation
        status = api.get_api_status()
        self.uptime.update(status)
        return status

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

        if not self.username:
            raise ControllerError("Username is required.")
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
        # if the slug of another document changed at this point
        # it's possible to have two documents with the same slug
        # registered. but it should be rare enough in reality.

        if self.slug:
            _id = self.find(self.slug)
            if _id and _id != self._id:  # another doc same slug.
                raise ConflictError("Slug is already registered.")

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

        doc.meta.id = self._id
        doc._meta.url = self.url
        doc._meta.username = self.username
        doc._meta.date_created = self.date_created
        doc._meta.last_updated = self.last_updated
        doc._meta.slug = self.slug

        doc.save(skip_empty=False)

        return self._id

    @property
    def version(self):
        """
        API specification format version name.
        This field decides how it is saved in ES.
        """
        if "openapi" in self._data:
            return "openapi"
        if "swagger" in self._data:
            return "swagger"
        return None

    def _validate_dispatch(self):

        if not self.version:
            raise ControllerError("Unknown version.")

        if self.version == "openapi":
            doc = OpenAPI(self._data)
        else:  # then it must be swagger
            doc = Swagger(self._data)

        return doc
