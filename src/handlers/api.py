import asyncio
import json
import logging
import os

import bmt
from biothings.utils import serializer
from biothings.web.auth.authn import BioThingsAuthnMixin
from biothings.web.handlers import BaseAPIHandler, QueryHandler
from biothings.web.handlers.query import BiothingHandler, capture_exceptions
from biothings.web.settings.default import QUERY_KWARGS
from tornado.httpclient import AsyncHTTPClient
from tornado.template import Loader
from tornado.web import Finish, HTTPError

from controller import SmartAPI
from controller.exceptions import ControllerError, NotFoundError
from pipeline import MetaKGQueryPipeline
from utils.downloader import DownloadError, download_async
from utils.http_error import SmartAPIHTTPError
from utils.metakg.biolink_helpers import get_expanded_values
from utils.metakg.cytoscape_formatter import CytoscapeDataFormatter
from utils.metakg.export import edges2graphml
from utils.metakg.parser import MetaKGParser
from utils.metakg.path_finder import MetaKGPathFinder
from utils.notification import SlackNewAPIMessage, SlackNewTranslatorAPIMessage

logger = logging.getLogger("smartAPI")


def github_authenticated(func):
    """
    RegistryHandler Decorator
    """

    def _(self, *args, **kwargs):
        if not self.current_user:
            self.send_error(message="You must log in first.", status_code=401)
            return
        return func(self, *args, **kwargs)

    return _


class BaseHandler(BioThingsAuthnMixin, BaseAPIHandler):
    pass


class AuthHandler(BaseHandler):
    def set_cache_header(self, cache_value):
        # disabel cache for auth-related handlers
        self.set_header("Cache-Control", "private, max-age=0, no-cache")


class UserInfoHandler(AuthHandler):
    """ "Handler for /user_info endpoint."""

    def get(self):
        # Check for user cookie
        if self.current_user:
            self.write(self.current_user)
        else:
            # Check for WWW-authenticate header
            header = self.get_www_authenticate_header()
            if header:
                self.clear()
                self.set_header("WWW-Authenticate", header)
                self.set_status(401, "Unauthorized")
                # raising HTTPError will cause headers to be emptied
                self.finish()
            else:
                raise HTTPError(status_code=403)


class LoginHandler(AuthHandler):
    def get(self):
        self.redirect(self.get_argument("next", "/"))


class LogoutHandler(AuthHandler):
    def get(self):
        self.clear_cookie("user")
        self.redirect(self.get_argument("next", "/"))


class ValidateHandler(BaseHandler):
    """
    Validate a Swagger/OpenAPI document.
    Support three types of requests.

    GET /api/validate?url=<url>

    POST /api/validate
    url=<url>

    POST /api/validate
    {
        "openapi": "3.0.0",
        ...
    }
    """

    name = "validator"
    kwargs = {
        "GET": {"url": {"type": str, "location": "query", "required": True}},
        "POST": {"url": {"type": str, "location": "form"}},
    }

    # TODO
    # maybe this module should return 200 for all retrievable files?
    # when a document doesn't pass validation, maybe it's better to
    # indicate it by a field "passed": True/False instead of sharing
    # the same status code as missing a url parameter here.

    async def get(self):
        if self.request.body:
            raise HTTPError(status_code=400, reason="GET takes no request body.")

        raw = await self.download(self.args.url)
        self.validate(raw)

    async def post(self):
        if self.args.url:
            raw = await self.download(self.args.url)
        else:  # then treat the request body as raw
            raw = self.request.body

        self.validate(raw)

    async def download(self, url):
        try:
            file = await download_async(url)
        except DownloadError as err:
            raise HTTPError(400, reason=str(err))
        else:  # other file info irrelevant for validation
            return file.raw

    def validate(self, raw):
        try:
            smartapi = SmartAPI(SmartAPI.VALIDATION_ONLY)
            smartapi.raw = raw
            smartapi.validate()
        except (ControllerError, AssertionError) as err:
            raise SmartAPIHTTPError(400, reason=str(err))
        else:
            self.finish({"success": True, "details": f"valid SmartAPI ({smartapi.version}) metadata."})


class SmartAPIHandler(BaseHandler, BiothingHandler):
    kwargs = {
        "*": BiothingHandler.kwargs["*"],
        "PUT": {
            "slug": {"type": str, "default": None},
        },
        "POST": {
            "url": {"type": str, "required": True},
            "dryrun": {"type": bool, "default": False},
        },
    }

    @github_authenticated
    async def post(self):
        """
        Add an API document
        """

        if SmartAPI.find(self.args.url, "url"):
            raise HTTPError(status_code=409)

        try:
            file = await download_async(self.args.url)
        except DownloadError as err:
            raise HTTPError(status_code=400, reason=str(err)) from err

        try:
            smartapi = SmartAPI(self.args.url)
            smartapi.raw = file.raw
            smartapi.validate()
        except (ControllerError, AssertionError) as err:
            raise HTTPError(status_code=400, reason=str(err)) from err

        if self.args.dryrun:
            raise Finish({"success": True, "details": f"[Dryrun] Valid {smartapi.version} Metadata"})

        try:
            smartapi.username = self.current_user["login"]
            smartapi.refresh(file)  # populate webdoc meta
            _id = smartapi.save()
        except ControllerError as err:
            raise HTTPError(status_code=400, reason=str(err)) from err
        else:
            self.finish({"success": True, "_id": _id})
            await self._notify(smartapi)

    async def _notify(self, smartapi):
        if self.settings.get("debug"):
            return

        client = AsyncHTTPClient()
        kwargs = {
            "_id": smartapi._id,
            "name": dict(smartapi).get("info", {}).get("title", "<Notitle>"),
            "description": dict(smartapi).get("info", {}).get("description", "")[:120] + "...",
            "username": smartapi.username,
        }
        try:
            # NOTE
            # SLACK_WEBHOOKS = [
            #     {"webhook": <url>}
            #     {"webhook": <url>, "tags": "translator"} # project specific
            # ]
            for slack in getattr(self.web_settings, "SLACK_WEBHOOKS", []):
                if "tags" in slack:
                    if slack["tags"] == "translator":
                        if "x-translator" in smartapi["info"]:
                            res = await client.fetch(
                                slack["webhook"],
                                method="POST",
                                headers={"content-type": "application/json"},
                                body=json.dumps(SlackNewTranslatorAPIMessage(**kwargs).compose()),
                            )
                            logging.info(res.code)
                            logging.info(res.body)

                    # elif slack["tags"] == <other>:
                    #   pass

                else:  # typical case
                    res = await client.fetch(
                        slack["webhook"],
                        method="POST",
                        headers={"content-type": "application/json"},
                        body=json.dumps(SlackNewAPIMessage(**kwargs).compose()),
                    )
                    logging.info(res.code)
                    logging.info(res.body)

        except Exception as exc:
            logging.error(str(exc))

    @github_authenticated
    async def put(self, _id):
        """
        Add/Update the URL slug:
            PUT {"slug": "new_slug"}
        Remove a URL slug:
            PUT {"slug": "" }
        Refresh a document:
            PUT {}
        """

        try:
            smartapi = SmartAPI.get(_id)
        except NotFoundError:
            raise HTTPError(status_code=404)

        if smartapi.username != self.current_user["login"]:
            raise HTTPError(status_code=403)

        if self.args.slug is not None:
            if self.args.slug in {"api"}:  # reserved
                raise HTTPError(status_code=400, reason="slug is reserved")

            try:  # update slug
                smartapi.slug = self.args.slug or None
                smartapi.save()

            except (ControllerError, ValueError) as err:
                raise HTTPError(status_code=400, reason=str(err)) from err

            self.finish({"success": True})

        else:  # refresh
            file = await download_async(smartapi.url, raise_error=False)
            code = smartapi.refresh(file)
            smartapi.save()

            try:
                status = smartapi.webdoc.STATUS(code)
                status = status.name.lower()
            except ValueError:
                status = "nofile"  # keep the original copy

            self.finish({"success": code in (200, 299), "status": status, "code": code})

    @github_authenticated
    def delete(self, _id):
        """
        Delete API
        """

        try:
            smartapi = SmartAPI.get(_id)
        except NotFoundError:
            raise HTTPError(status_code=404)

        if smartapi.username != self.current_user["login"]:
            raise HTTPError(status_code=403)

        try:
            _id = smartapi.delete()
        except ControllerError as err:
            raise HTTPError(status_code=400, reason=str(err)) from err

        self.finish({"success": True, "_id": _id})


class ValueSuggestionHandler(BaseHandler):
    """
    Handle field aggregation for UI suggestions
    """

    kwargs = {
        "GET": {"field": {"type": str, "required": True}},
    }

    name = "value_suggestion"

    def get(self):
        """
        /api/suggestion?field=
        Returns aggregations for any field provided
        Used for tag:count on registry
        """
        res = SmartAPI.get_tags(self.args.field)
        self.finish(res)


class UptimeHandler(BaseHandler):
    """
    Check uptime status for a registered API

    GET /api/uptime?id=<id>

    POST /api/uptime
    id=<id>
    """

    kwargs = {
        "GET": {"id": {"type": str, "location": "query", "required": True}},
        "POST": {"id": {"type": str, "location": "form", "required": True}},
    }

    name = "uptime_checker"

    @github_authenticated
    def get(self):
        if self.request.body:
            raise HTTPError(status_code=400, reason="GET takes no request body.")

        if self.args.id:
            try:
                smartapi = SmartAPI.get(self.args.id)
                if smartapi.username != self.current_user["login"]:
                    raise HTTPError(status_code=403)
                status = smartapi.check()
                smartapi.save()
            except NotFoundError:
                raise HTTPError(status_code=404)
            except (ControllerError, AssertionError) as err:
                raise HTTPError(status_code=400, reason=str(err))
            else:
                self.finish({"success": True, "details": status})
        else:
            raise HTTPError(status_code=400, reason="Missing required parameter: id")

    @github_authenticated
    def post(self):
        if self.args.id:
            try:
                smartapi = SmartAPI.get(self.args.id)
                if smartapi.username != self.current_user["login"]:
                    raise HTTPError(status_code=403)
                status = smartapi.check()
                smartapi.save()
            except NotFoundError:
                raise HTTPError(status_code=404)
            except (ControllerError, AssertionError) as err:
                raise HTTPError(status_code=400, reason=str(err))
            else:
                self.finish({"success": True, "details": status})
        else:
            raise HTTPError(status_code=400, reason="Missing required form field: id")


class MetaKGHandlerMixin:
    """
    Mixin to provide reusable logic for filtering API information.
    """
    def get_filtered_api(self, api_dict):
        """Extract and return filtered API information."""
        api_info = api_dict.get("api", api_dict)  # Handle both formats

        # Default to False if not present
        bte = self.args.bte
        api_details = self.args.api_details

        # Default structure to preserve top-level keys
        filtered_dict = {
            key: api_dict.get(key)
            for key in ["subject", "object", "predicate", "subject_prefix", "object_prefix"]
            if key in api_dict
        }

        # Determine filtered API structure based on `bte` and `api_details`
        if bte and not api_details:
            # When bte is True and api_details is False, include only minimal API info
            filtered_api = {
                **({"name": api_info.get("name")} if "name" in api_info else {}),
                **(
                    {"smartapi": {"id": api_info.get("smartapi", {}).get("id", None)}}
                    if "smartapi" in api_info
                    else {"smartapi": {"id": None}}
                ),
                "bte": api_info.get("bte", {}),
            }
        elif api_details:
            # When api_details is True, include more detailed information
            filtered_api = api_info.copy()
            if not bte:
                filtered_api.pop("bte", None)

            # Handle case where "ui" key exists and ends with "None"
            if filtered_api.get('smartapi', {}).get("ui", "").endswith("/None"):
                filtered_api["smartapi"]["ui"] = None
        else:
            # Default: No bte and no api_details - just minimal API info
            filtered_api = {
                **({"name": api_info.get("name")} if "name" in api_info else {}),
                **(
                    {"smartapi": {"id": api_info.get("smartapi", {}).get("id", None)}}
                    if "smartapi" in api_info
                    else {"smartapi": {"id": None}}
                ),
            }

        # Add the filtered 'api' key to the preserved top-level structure
        filtered_dict["api"] = filtered_api

        # Remove 'bte' from 'api' and move it to the top level
        if "bte" in filtered_dict["api"]:
            filtered_dict["bte"] = filtered_dict["api"].pop("bte")

        return filtered_dict


class MetaKGQueryHandler(QueryHandler, MetaKGHandlerMixin):
    """
    Support metakg queries with biolink model's semantic descendants

    Allowed query by fields: subject, object, predicate
    If expand is passed, will use Biolink Model Toolkit to get these terms' descendants, and queries by them instead.
    """

    name = "metakg"
    kwargs = {
        "*": {
            **QUERY_KWARGS["*"],
            # overwrite format parameter config to add "graphml" option
            "format": {
                "type": str,
                "default": "json",
                "enum": ("json", "yaml", "html", "msgpack", "graphml"),
            },
        },
        "GET": {
            **QUERY_KWARGS.get("GET", {}),
            "subject": {"type": list, "max": 1000},
            "object": {"type": list, "max": 1000},
            "node": {"type": list, "max": 1000},  # either subject or object
            "predicate": {"type": list, "max": 1000, "alias": "edge"},
            "size": {"type": int, "max": 5000, "alias": "limit"},  # overwrite size limit for graphml export
            "download": {"type": bool, "default": True},
            "expand": {
                "type": list,
                "max": 6,
                "default": [],
                "enum": ["subject", "object", "predicate", "node", "edge", "all"],
            },
            "html_view": {
                "type": str,
                "default": "cytoscape",
                "enum": ("json", "cytoscape"),
                "alias": "default_view"
            },
            "html_header": {
                "type": bool,
                "default": True,
                "alias": "header"
            },
            "consolidated": {"type": bool, "default": True},
            "api_details": {"type": bool, "default": False},
            "bte": {"type": bool, "default": False},
        },
    }

    def initialize(self, *args, **kwargs):
        super().initialize(*args, **kwargs)
        # change the default query pipeline from self.biothings.pipeline
        self.pipeline = MetaKGQueryPipeline(ns=self.biothings)
        self.biolink_model_toolkit = bmt.Toolkit()

    @capture_exceptions
    async def get(self, *args, **kwargs):
        # Setup expanded fields
        expanded_fields = {"subject": False, "object": False, "predicate": False, "node": False}
        if "edge" in self.args.expand and "predicate" not in self.args.expand:
            # edge is an alias of predicate, if edge is in expand, add predicate to expand
            self.args.expand.remove("edge")
            self.args.expand.append("predicate")
        if self.args.expand:
            for field in expanded_fields:
                if field in self.args.expand or "all" in self.args.expand:
                    expanded_fields[field] = True

        for field in expanded_fields:
            value_list = getattr(self.args, field)
            if not value_list:
                continue
            value_list = get_expanded_values(value_list, self.biolink_model_toolkit) if expanded_fields[field] else value_list
            setattr(self.args, field, value_list)

        await super().get(*args, **kwargs)

    def process_apis(self, apis):
        """Process each API dict based on provided args."""
        if isinstance(apis, list):
            for i, api_dict in enumerate(apis):
                filtered_api = self.get_filtered_api(api_dict)
                apis[i] = filtered_api
        elif isinstance(apis, dict):
            if 'bte' in apis:
                # update dict for new format
                apis['api']['bte'] = apis.pop('bte')
            api_dict = apis["api"]
            filtered_api = self.get_filtered_api(api_dict)
            apis["api"] = filtered_api

    def write(self, chunk):
        """
        Overwrite the biothings query handler to ...
        Write out graphml format (&format=graphml)
        Set &download=True to download .graphml file automatically, can disable (&download=False)
        Reshape results for Cytoscape-ready configuration rendering on the front-end. (&format=html)
        Added index flag for index variability, set default to MetaKGConsolidated (&consolidated=1)
        Added filtering for api and bte details (&api_details=1, &bte=1)
        """
        try:
            if self.args.consolidated:
                for data_hit in chunk['hits']:
                    self.process_apis(data_hit['api'])
            else:
                for hit_dict in chunk['hits']:
                    self.process_apis(hit_dict)

            if self.format == "graphml":
                chunk = edges2graphml(
                    chunk, self.request.uri, self.request.protocol, self.request.host, edge_default="directed"
                )
                self.set_header("Content-Type", "text/graphml; charset=utf-8")
                if self.args.download:
                    self.set_header("Content-Disposition", 'attachment; filename="smartapi_metakg.graphml"')

                return super(BaseAPIHandler, self).write(chunk)

            if self.format == "html":
                # setup template
                template_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
                loader = Loader(template_path)
                template = loader.load("cytoscape.html")
                # initial counts
                shown = 0
                available = 0
                graph_data = []
                # if no hits template will show response as is and
                # display a help message.
                if "total" in chunk and "hits" in chunk:
                    available = chunk['total']
                    shown = len(chunk['hits'])
                    # reformat data
                    cdf = CytoscapeDataFormatter(chunk['hits'])
                    graph_data = serializer.to_json(cdf.get_data())
                # generate global template variable with graph data
                result = template.generate(
                    data=graph_data,
                    response=serializer.to_json(chunk),
                    shown=shown,
                    available=available,
                    default_view=serializer.to_json(self.args.html_view),
                    header=serializer.to_json(self.args.html_header)
                )
                self.set_header("Content-Type", "text/html; charset=utf-8")
                return super(BaseAPIHandler, self).write(result)

        except Exception as exc:
            logger.warning(exc)

        super().write(chunk)


class MetaKGPathFinderHandler(QueryHandler):
    """
    A handler for querying paths in a knowledge graph using the custom MetaKGPathFinder module.

    Attributes:
    - name: Unique identifier for this handler.
    - kwargs: Configuration for GET request parameters.

    The primary GET method accepts the required 'subject', 'object', and 'cutoff'(default=3) parameters, then retrieves
    and returns paths in JSON format between the specified nodes up to the given 'cutoff' length.
    """

    name = "metakgpathfinder"
    kwargs = {
        "GET": {
            **QUERY_KWARGS.get("GET", {}),
            "subject": {"type": str, "required": True, "max": 1000},
            "object": {"type": str, "required": True, "max": 1000},
            "predicate": {"type": list, "max": 10, "default": []},
            "cutoff": {"type": int, "default": 3, "max": 5},
            "api_details": {"type": bool, "default": False},
            "rawquery": {"type": bool, "default": False},
            "bte": {"type": bool, "default": False},
            "expand": {
                "type": list,
                "max": 6,
                "default": [],
                "enum": ["subject", "object", "predicate", "node", "edge", "all"]
            }
        },
    }

    def initialize(self, *args, **kwargs):
        super().initialize(*args, **kwargs)
        # change the default query pipeline from self.biothings.pipeline
        self.pipeline = MetaKGQueryPipeline(ns=self.biothings)
        self.biolink_model_toolkit = bmt.Toolkit()

    def setup_pathfinder_rawquery(self, expanded_fields):
        # JSON-structured summary of operations and criteria applied
        operations_summary = {
            "input_parameters": {},
            "expansion_logic": {},
            "search_criteria": []
        }

        # Include original query parameters
        operations_summary["input_parameters"] = {
            "subject": self.args.subject,
            "object": self.args.object,
            "predicate": getattr(self.args, 'predicate', None)  # Including predicate if provided
        }

        # Detail the expansion logic in a way that explains what expansions are applied
        operations_summary["expansion_logic"] = {
            "expand_subject": "subject" in self.args.expand or "all" in self.args.expand or "node" in self.args.expand,
            "expand_object": "object" in self.args.expand or "all" in self.args.expand or "node" in self.args.expand,
            "expand_predicate": "predicate" in self.args.expand,
        }

        # Summarize the search criteria based on expanded fields
        for field, values in expanded_fields.items():
            if values:  # Ensure values exist for the field before adding
                operations_summary["search_criteria"].append({
                    "field": field,
                    "description": f"Expanding '{field}' to include {len(values)} variant(s)",
                    "values": values
                })

        # The operations_summary is already in a format that can be directly returned as JSON
        return operations_summary

    @capture_exceptions
    async def get(self, *args, **kwargs):

        # Check if subject and object are the same - not allowed
        if self.args.subject == self.args.object:
            raise ValueError("Subject and object must be different.")

        query_data = {"q": self.args.q}

        # Initialize with the original subject and object, and setup for expansion
        expanded_fields = {
            "subject": [self.args.subject],
            "object": [self.args.object],
        }

        # Check if expansion is requested
        if self.args.expand:
            # Define a set for fields affected by 'node' and 'all' for simpler updates
            common_fields = {"subject", "object"}

            # Initialize expandable_fields based on 'node' or 'all' presence
            expandable_fields = set()
            if "node" in self.args.expand or "all" in self.args.expand:
                expandable_fields.update(common_fields)
            if "edge" in self.args.expand or "all" in self.args.expand:
                expandable_fields.add("predicate")

            # Add specific fields if mentioned explicitly
            expandable_fields.update({field for field in ["subject", "object", "predicate"] if field in self.args.expand})

            # Expand the fields as required
            for field in expandable_fields:
                # Use the built-in utility function, get_expanded_values, to expand the fields
                expanded_fields[field] = get_expanded_values(getattr(self.args, field), self.biolink_model_toolkit)

        # Initalize pathfinder
        pathfinder = MetaKGPathFinder(query_data=query_data, expanded_fields=expanded_fields)

        # Initialize the pathfinder results list
        paths_with_edges = []

        # Run get_paths method to retrieve paths and edges
        paths_with_edges = pathfinder.get_paths(
            # expanded_fields=expanded_fields,
            cutoff=self.args.cutoff,
            api_details=self.args.api_details,
            predicate_filter=self.args.predicate,
            bte=self.args.bte
        )

        # # Error check path results
        if "error" in paths_with_edges:
            raise HTTPError(400, reason=str(paths_with_edges["error"]))

        # Check if rawquery parameter is true -- respond with correct output
        if self.args.rawquery:
            raw_query_output = self.setup_pathfinder_rawquery(expanded_fields)
            self.write(raw_query_output)
            return
        res = {
            "total": len(paths_with_edges),
            "paths": paths_with_edges,
        }
        await asyncio.sleep(0.01)
        self.finish(res)


class MetaKGParserHandler(BaseHandler, MetaKGHandlerMixin):
    """
        Handles parsing of SmartAPI metadata from a given URL or request body.

        This handler processes SmartAPI metadata and returns structured,
        cleaned results based on the specified query parameters.

        Supported HTTP methods:
        - **GET**: Parses metadata from a provided URL.
        - **POST**: Parses metadata from the request body.

        Query Parameters:
        - `url` (str, required): The URL of the SmartAPI metadata to parse.
            Maximum length: 1000 characters.
        - `api_details` (bool, optional, default: `False`):
            Whether to return detailed API information.
        - `bte` (bool, optional, default: `False`):
            Whether to include BTE (BioThings Explorer) specific metadata.
    """

    kwargs = {
        "*": {
            "api_details": {"type": bool, "default": False},
            "bte": {"type": bool, "default": False},
        },
        "GET": {
            "url": {
                "type": str,
                "required": True,
                "max": 1000,
                "description": "URL of the SmartAPI metadata to parse"
            },
        },
    }

    def initialize(self, *args, **kwargs):
        super().initialize(*args, **kwargs)
        # change the default query pipeline from self.biothings.pipeline
        self.pipeline = MetaKGQueryPipeline(ns=self.biothings)

    def process_apis(self, apis):
        """Process each API dict based on provided args."""
        if isinstance(apis, list):
            for i, api_dict in enumerate(apis):
                filtered_api = self.get_filtered_api(api_dict)
                apis[i] = filtered_api
        elif isinstance(apis, dict):
            if "bte" in apis:
                # Update dict for new format
                apis["api"]["bte"] = apis.pop("bte")
            api_dict = apis["api"]
            filtered_api = self.get_filtered_api(api_dict)
            apis["api"] = filtered_api
        return apis

    async def get(self, *args, **kwargs):
        url = self.args.url
        parser = MetaKGParser()

        try:
            parsed_metakg = parser.get_metakg(url=url)
        except DownloadError:
            self.write_error(400, reason="There was an error downloading the data from the given url.")
        except (ValueError, TypeError) as err:
            self.write_error(
                status_code=400,
                reason="The data retrived from the given url is not a valid JSON or YAML object.",
                message=str(err)
            )

        # Apply filtering -- if data found
        if parsed_metakg:
            for i, api_dict in enumerate(parsed_metakg):
                parsed_metakg[i] = self.get_filtered_api(api_dict)

        # Add url to metadata if api_details is set to 1
        if self.args.api_details:
            for data_dict in parsed_metakg:
                if "metadata" in data_dict["api"]["smartapi"] and data_dict["api"]["smartapi"]["metadata"] is None:
                    data_dict["api"]["smartapi"]["metadata"] = url

        response = {
            "total": len(parsed_metakg),
            "hits": parsed_metakg,
        }

        self.finish(response)

    async def post(self, *args, **kwargs):
        content_type = self.request.headers.get("Content-Type", "").lower()
        if content_type in ["application/json", "application/x-yaml"]:
            # if content type is set properly, it should have alrady been parsed
            metadata_from_body = self.args_json or self.args_yaml
        elif self.request.body:
            # if request body is provided but no proper content type is set
            # we will parse it as YAML anyway
            metadata_from_body = self._parse_yaml()
        else:
            metadata_from_body = None

        if metadata_from_body:
            # Process the parsed metadata
            parser = MetaKGParser()
            parsed_metakg = parser.get_metakg(metadata_from_body)

            # Apply filtering to the combined data
            if parsed_metakg:
                for i, api_dict in enumerate(parsed_metakg):
                    parsed_metakg[i] = self.get_filtered_api(api_dict)

            # Send the response back to the client
            response = {
                "total": len(parsed_metakg),
                "hits": parsed_metakg,
            }

            self.finish(response)
        else:
            self.write_error(
                status_code=400,
                reason="Request body cannot be empty.",
                message="Please provide a valid JSON/YAML object in the request body."
            )
