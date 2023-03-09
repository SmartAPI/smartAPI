from abc import ABC, abstractmethod
from collections import UserDict, namedtuple
from collections.abc import Iterable, Mapping
from datetime import timezone
from email.utils import parsedate_to_datetime as parsedt

# from itertools import repeat
from urllib.parse import urlparse

import certifi
import requests
from tornado import httpclient

from utils import decoder

# TODO should capture ERR_CONNECTION_TIMED_OUT message


class DownloadError(Exception):
    """Error fetching data from url"""


File = namedtuple(
    "File",
    (
        "status",  # HTTP status code
        "raw",  # response body as bytes
        "etag",  # stripped ETag hash in header
        "date",  # response time in header
    ),
)

# PYTHON 3.7 - MARK A
# File = namedtuple("File", (
#     "status",  # HTTP status code
#     "raw",  # response body as bytes
#     "etag",  # stripped ETag hash in header
#     "date",  # response time in header
# ), defaults=repeat(None, 4))

# NOTE may also be helpful to record
# response expiration time in header
# content-type to facilitate parsing


def file_name(url):
    url = urlparse(url)
    return url.path.split("/")[-1]


def file_extension(url):
    filename = file_name(url)
    if "." in filename:
        return filename.split(".")[-1]
    return None  # no extension


class ResponseParser(ABC):
    def __init__(self, response):
        assert hasattr(response, "headers")
        assert isinstance(response.headers, Mapping)
        self._response = response

    @abstractmethod
    def get_status(self):
        pass

    @abstractmethod
    def get_raw(self):
        pass

    def get_etag(self):
        etag = self._response.headers.get("ETag", "")
        return etag.strip('W/"') or None

    def get_date(self):
        # https://docs.python.org/3/library/email.utils.html#email.utils.parsedate_to_datetime

        _ts = self._response.headers.get("Date")

        # NOTE
        # Use the server time instead of the local time is an arbitary decision here.
        # Add more checking logic here to contain the error if this matters.

        try:
            return parsedt(_ts).replace(tzinfo=timezone.utc)
        except TypeError:
            return None


class RequestsParser(ResponseParser):
    # https://requests.readthedocs.io/en/latest/api/#requests.Response

    def __init__(self, response):
        assert isinstance(response, requests.Response)
        super().__init__(response)

    def get_status(self):
        return self._response.status_code

    def get_raw(self):
        return self._response.content


class TornadoParser(ResponseParser):
    # https://www.tornadoweb.org/en/stable/httpclient.html#response-objects

    def __init__(self, response):
        assert isinstance(response, httpclient.HTTPResponse)
        super().__init__(response)

    def get_status(self):
        return self._response.code

    def get_raw(self):
        return self._response.body


# TODO REQUIRE ADDITIONAL TESTING TO UNDERSTAND ERROR TYPES


def download(url, timeout=5, raise_error=True):
    try:
        response = requests.get(url, timeout=timeout)
        if raise_error:
            response.raise_for_status()
        result = RequestsParser(response)
    except requests.exceptions.HTTPError as err:
        raise DownloadError(str(err)) from err
    except requests.exceptions.RequestException as err:
        if raise_error:
            raise DownloadError(str(err)) from err
        return File(599, None, None, None)  # MARK A
    else:
        return File(status=result.get_status(), raw=result.get_raw(), etag=result.get_etag(), date=result.get_date())


async def download_async(url, timeout=20, raise_error=True):
    client = httpclient.AsyncHTTPClient()
    try:
        response = await client.fetch(url, request_timeout=timeout, raise_error=raise_error, ca_certs=certifi.where())
        result = TornadoParser(response)
    except httpclient.HTTPClientError as err:
        raise DownloadError(str(err)) from err
    except IOError as err:
        if raise_error:
            raise DownloadError(type(err).__name__) from err
        return File(599, None, None, None)  # MARK A
    else:
        return File(status=result.get_status(), raw=result.get_raw(), etag=result.get_etag(), date=result.get_date())


def download_mapping(url):
    response = requests.get(url)
    response.raise_for_status()

    return decoder.to_dict(stream=response.content, ext=file_extension(url), ctype=response.headers.get("Content-Type"))


class Downloader(UserDict):
    """
    Container for remote mapping files.
    Support dictionary-like access.
    """

    def download(self, name, url):
        if isinstance(name, Iterable):
            for _name, _url in zip(name, url):
                self.data[_name] = download_mapping(_url)
            return

        if not name:  # use filename without extension
            name = file_name(url)
            ext = file_extension(url) or ""
            name = name[: -len(ext)]  # TODO NOT YET TESTED

        self.data[name] = download_mapping(url)
