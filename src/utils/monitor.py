"""
    API Uptime Monitor

    Author:
        Kevin Xin
        Amiteshk Sharma

    Status:
        Pass,
        Fail,
        Incompatible,
        Unknown

"""
import json
import logging
import traceback
from enum import Enum
from pprint import pformat
from textwrap import shorten

import requests

# pylint:disable=import-error, ungrouped-imports
from requests.packages.urllib3.exceptions import InsecureRequestWarning  # pyright: ignore [reportMissingImports]

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  # pylint:disable=no-member


logger = logging.getLogger("utils.monitor")


def _shorten(s, width=80):  # pylint: disable=invalid-name
    """a helper function to shorten long string to 80 max-length"""
    return shorten(s, width=width, placeholder="...")


class Cors(Enum):
    """enums class to represent outcomes for cors check"""

    ENABLED = "CORS-Enabled"
    DISABLED = "CORS-Disabled"
    UNKNOWN = "CORS-Unknown"


# provide information on total APIs with CORS support
# takes in the total count of APIs provided


class CorsCounter:
    """Count CORS status for all registered APIs"""

    def __init__(self, total_api_count):
        self._enabled = 0  # number of CORS-enabled APIs
        self._disabled = 0  # number of CORS-disabled APIs
        self._unknown = 0  # number of CORS-unknown APIs
        self.total_apis = total_api_count

    def increment_count(self, count):
        """used to increment the correct count"""
        try:
            if count == -1:
                self._unknown += 1
            elif count > 0:
                self._enabled += 1
            else:
                self._disabled += 1
        except TypeError:
            logger.error("CorsCounter.CorsStatus: Please pass in a int. ")

    def __str__(self):
        enabled = f"The total number of CORS-enabled APIs out of ({self.total_apis}): ({self._enabled})\n"
        disabled = f"The total number of CORS-disabled APIs out of ({self.total_apis}): ({self._disabled})\n"
        unknown = f"The total number of CORS-unknown APIs out of ({self.total_apis}): ({self._unknown})\n"

        return enabled + disabled + unknown


class DictQuery(dict):
    """
    Extract the value from nested json based on path
    """

    def get(self, path, default=None):
        keys = path.split("/")
        val = None

        for key in keys:
            if val:
                if isinstance(val, list):
                    val = [v.get(key, default) if v else None for v in val]  # pylint:disable=not-an-iterable
                else:
                    val = val.get(key, default)
            else:
                val = dict.get(self, key, default)

            if not val:
                break

        return val


class API:
    """
    An API corresponding to an es document
    """

    def __init__(self, api_doc):
        # default status of API is unknown, since some APIs doesn't provide
        # examples as values for parameters
        self._api_status = None
        self._cors_status = None
        self._total_cors = 0  # count the number of CORS responses
        self._uptime_msg = []
        try:
            self.name = api_doc["info"]["title"]
        except KeyError:
            self.name = "No name specified"
        try:
            self.id = api_doc["_id"]  # pylint: disable=invalid-name
        except KeyError:
            self.id = "no ID specified"
        try:
            self.api_server = api_doc["servers"][0]["url"]
        except KeyError:
            self.api_server = None
            self.api_status = "incompatible"
        if "paths" not in api_doc:
            self.api_status = "incompatible"
        self.components = api_doc.get("components")
        self.endpoints_info = api_doc.get("paths")
        self.logger = logger

    def test_endpoint(self, _endpoint, _endpoint_info):
        """
        Test an endpoint and return its status as:
            - pass
            - fail
            - unknown

        """
        endpoint_doc = {
            "name": "/".join(s.strip("/") for s in (self.api_server, _endpoint)),
            "components": self.components,
        }
        if "get" in _endpoint_info:
            endpoint_doc["method"] = "GET"
            endpoint_doc["params"] = _endpoint_info.get("get").get("parameters", [])
        elif "post" in _endpoint_info:
            endpoint_doc["method"] = "POST"
            endpoint_doc["params"] = _endpoint_info.get("post").get("parameters", [])
            endpoint_doc["requestbody"] = _endpoint_info["post"].get("requestBody")
        if "parameters" in _endpoint_info:
            # merge common parameters if defined at the endpoint root level
            endpoint_doc["params"] = _endpoint_info.get("parameters") + endpoint_doc.get("params", [])
        if "params" in endpoint_doc or endpoint_doc.get("requestbody"):
            endpoint = Endpoint(endpoint_doc)
            try:
                response = endpoint.make_api_call()
            except requests.RequestException as err:  # pylint: disable=broad-except
                _msg = f"🔴 {_endpoint}: (requestexception) {repr(err)}"
                self.logger.error(_msg)
                self._uptime_msg.append(_msg)
                return "fail"
            else:
                if isinstance(response, requests.models.Response):
                    status = endpoint.check_response_status(response)
                    cors = endpoint.check_cors_status(response)

                    if cors == 0:
                        self._cors_status = Cors.ENABLED.value
                        self._total_cors = 1
                    else:
                        self._cors_status = Cors.DISABLED.value

                    if status < 400:
                        _msg = f"🟢 {status}: ({_endpoint}) All good!"
                        self._uptime_msg.append(_msg)
                        self.logger.debug(_msg)
                        return "pass"
                    elif status == 501:
                        # label the endpoint as "unknown", if the request returns 501 NOT IMPLEMENTED
                        _msg = f"🟠 {_endpoint}: ({status}) (skipped) {_shorten(response.text)}"
                        self._uptime_msg.append(_msg)
                        self.logger.info(
                            "%s returns 501 NOT IMPLEMENTED, therefore skipped.",
                            _endpoint,
                        )
                        return "unknown"
                    else:
                        # any status code >= 400, label as "fail"
                        _msg = f"🔴 {_endpoint}: ({status}) {_shorten(response.text)}"
                        self._uptime_msg.append(_msg)
                        self.logger.debug(_msg)
                        return "fail"
                else:
                    # endpoint call failure
                    _msg = f"🟠 {_endpoint}: (skipped) Missing Required Params/Body"
                    self._uptime_msg.append(_msg)
                    self.logger.debug(_msg)
                    return "unknown"

    def check_api_status(self):
        """
        loop through each endpoint and extract parameter & example $ HTTP method information
        """
        self._api_status = "unknown"
        self._cors_status = Cors.UNKNOWN.value
        endpoint_results = []

        if not self.api_server:
            return

        for _endpoint, _endpoint_info in self.endpoints_info.items():
            res = None
            try:
                res = self.test_endpoint(_endpoint, _endpoint_info)
            except Exception as err:  # pylint: disable=broad-except
                # This is a final catch_all exception, just in case we miss any unhandled exception
                # It can be an error happened in the code. We should investigate and try to resolve it.
                _msg = f"🔴 {_endpoint}: (unhandled exception) {repr(err)}. Please contact us to resolve."
                self._uptime_msg.append(_msg)
                self.logger.error(_msg)
                print(traceback.format_exc())
                res = "fail"
            if res:
                endpoint_results.append(res)

        self.logger.info("Uptime check results:\n%s", pformat(self._uptime_msg))
        if "fail" in endpoint_results:
            self._api_status = "fail"
        else:
            self._api_status = "pass" if "pass" in endpoint_results else "unknown"
        self.logger.info("API uptime status: %s", self._api_status)

    def __str__(self):
        return f"{self.id}: {self._api_status}, {self._cors_status} ({self.name})"

    def get_api_status(self):
        """return the overall api status and a list of messages during the uptime checks"""
        return self._api_status, self._uptime_msg

    def get_cors_status(self):
        """return cors status"""
        return self._cors_status

    def get_total_cors(self):
        """TODO: the cors check feature to be completed"""
        if self._cors_status == "CORS-Unknown":
            return -1

        return self._total_cors


class Endpoint:
    """
    An API Endpoint
    """

    def __init__(self, endpoint_doc):
        self.endpoint_name = endpoint_doc["name"]
        self.method = endpoint_doc["method"]
        self.params = endpoint_doc["params"]
        self.requestbody = endpoint_doc.get("requestbody")
        self.components = endpoint_doc.get("components")

    def make_api_call(self):
        """Use requests package to send the example query to an API endpoint"""
        headers = {"User-Agent": "SmartAPI API status monitor"}
        url = self.endpoint_name
        # logger = logging.getLogger("utils.uptime.endpoint.make_api_call")
        if self.method == "GET":
            # handle API endpoint which uses GET HTTP method
            params = {}
            example = None
            paramsRequired = None  # pylint: disable=invalid-name
            logger.debug("self.params: %s", self.params)
            for _param in self.params:
                # replace parameter with actual example value to construct
                # an API call
                if "example" in _param:
                    # parameter in path
                    if _param["in"] == "path":
                        url = url.replace("{" + _param["name"] + "}", _param["example"])
                    # parameter in query
                    elif _param["in"] == "query":
                        params = {_param["name"]: _param["example"]}

                elif "required" in _param and _param["required"] is True:
                    paramsRequired = True  # pylint: disable=invalid-name
            # check required params
            if paramsRequired is True and not params:
                return False

            _request_kwargs = dict(
                url=url,
                verify=False,
                timeout=30,
                headers=headers,
            )
            if params:
                _request_kwargs["params"] = params
            response = requests.get(**_request_kwargs)
            logger.debug("[GET]: \n%s\n%s", pformat(_request_kwargs), response)
            return response

        # handle API endpoint which use POST HTTP method
        elif self.method == "POST":
            # handle API endpoint which uses POST HTTP method
            params = {}
            example = None
            bodyRequired = None  # pylint: disable=invalid-name
            # get example
            if self.requestbody:
                content = self.requestbody.get("content")
                if content and "application/json" in content:
                    headers["Content-Type"] = "application/json"
                    # 1st try to get the example value if already provided
                    example = content.get("application/json").get("example")
                    if not example:
                        schema = content.get("application/json").get("schema")
                        if schema:
                            # 2nd try to get example value from "schema" field
                            example = schema.get("example")
                            if schema.get("required", None):
                                # if schema.required is defined
                                bodyRequired = True  # pylint: disable=invalid-name
                            if not example:
                                ref = schema.get("$ref")
                                if ref:
                                    # 3nd try if schema is a reference to a component
                                    logger.debug(url)
                                    if ref.startswith("#/components/"):
                                        # check example
                                        component_path = ref[13:]
                                        component_path += "/example"
                                        logger.debug(
                                            "component path: %s",
                                            component_path,
                                        )
                                        example = DictQuery(self.components).get(component_path)
                                        logger.debug("example %s", example)
                                        # check required
                                        component_path = ref[13:]
                                        component_path += "/required"
                                        if DictQuery(self.components).get(component_path):
                                            bodyRequired = True  # pylint: disable=invalid-name

                    if isinstance(example, str):
                        # if example is a string, we try to jsonize it first,
                        # otherwise, keep it as it is
                        try:
                            example = json.loads(example)
                        except json.JSONDecodeError as err:
                            logger.debug("Error skipping decoding example %s", err)

                elif content and "application/x-www-form-urlencoded" in content:
                    headers["Content-Type"] = "application/x-www-form-urlencoded"
                    example = content.get("application/x-www-form-urlencoded").get("example")

                # check required body
                bodyRequired = bodyRequired or self.requestbody.get("required")  # pylint: disable=invalid-name
                if bodyRequired is True and not example:
                    return False

            # get params
            if self.params:
                paramsRequired = None  # pylint: disable=invalid-name
                for _param in self.params:
                    if "example" in _param:
                        if _param["in"] == "path":
                            url = url.replace("{" + _param["name"] + "}", _param["example"])
                        elif _param["in"] == "query":
                            params[_param["name"]] = _param["example"]
                    elif "required" in _param and _param["required"] is True:
                        paramsRequired = True  # pylint: disable=invalid-name
                # check required params
                if paramsRequired is True and not params:
                    return False

            _request_kwargs = dict(
                url=url,
                timeout=30,
                verify=False,
                headers=headers,
            )
            if params:
                _request_kwargs["params"] = params
            if example:
                if "json" in headers.get("Content-Type", ""):
                    _request_kwargs["json"] = example
                else:
                    _request_kwargs["data"] = example
            response = requests.post(**_request_kwargs)
            logger.debug("[POST]: \n%s\n%s", pformat(_request_kwargs), response)
            return response

        else:
            # we do not check non GET/POST endpoint
            # since they are typically related to data modifications, e.g. PUT, DELETE
            # or less commonly used, e.g. HEAD
            return False

    def check_response_status(self, response):
        """return response status code"""
        return response.status_code

    def check_cors_status(self, response):
        """return CORS status code: 1 - supported, 0 - not supported"""
        try:
            access_control = response.headers["Access-Control-Allow-Origin"]
            if access_control:
                return 0
        except KeyError:
            return 1
        else:
            return 1
