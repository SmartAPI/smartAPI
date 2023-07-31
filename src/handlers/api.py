import json
import logging
from typing import List, Union
import os

import bmt
from biothings.utils import serializer
from biothings.web.auth.authn import BioThingsAuthnMixin
from biothings.web.handlers import BaseAPIHandler, QueryHandler
from biothings.web.handlers.query import BiothingHandler, capture_exceptions
from biothings.web.settings.default import QUERY_KWARGS
from tornado.httpclient import AsyncHTTPClient
from tornado.web import Finish, HTTPError
from tornado.template import Loader

from controller import SmartAPI
from controller.exceptions import ControllerError, NotFoundError
from pipeline import MetaKGQueryPipeline
from utils.downloader import DownloadError, download_async
from utils.metakg.export import edges2graphml
from utils.metakg.cytoscape_formatter import CytoscapeDataFormatter
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
                raise HTTPError(403)


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
            raise HTTPError(400, reason="GET takes no request body.")

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
            raise HTTPError(400, reason=str(err))
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
            raise HTTPError(409)

        try:
            file = await download_async(self.args.url)
        except DownloadError as err:
            raise HTTPError(400, reason=str(err)) from err

        try:
            smartapi = SmartAPI(self.args.url)
            smartapi.raw = file.raw
            smartapi.validate()
        except (ControllerError, AssertionError) as err:
            raise HTTPError(400, reason=str(err)) from err

        if self.args.dryrun:
            raise Finish({"success": True, "details": f"[Dryrun] Valid {smartapi.version} Metadata"})

        try:
            smartapi.username = self.current_user["login"]
            smartapi.refresh(file)  # populate webdoc meta
            _id = smartapi.save()
        except ControllerError as err:
            raise HTTPError(400, reason=str(err)) from err
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
            raise HTTPError(404)

        if smartapi.username != self.current_user["login"]:
            raise HTTPError(403)

        if self.args.slug is not None:
            if self.args.slug in {"api"}:  # reserved
                raise HTTPError(400, reason="slug is reserved")

            try:  # update slug
                smartapi.slug = self.args.slug or None
                smartapi.save()

            except (ControllerError, ValueError) as err:
                raise HTTPError(400, reason=str(err)) from err

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
            raise HTTPError(404)

        if smartapi.username != self.current_user["login"]:
            raise HTTPError(403)

        try:
            _id = smartapi.delete()
        except ControllerError as err:
            raise HTTPError(400, reason=str(err)) from err

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
            raise HTTPError(400, reason="GET takes no request body.")

        if self.args.id:
            try:
                smartapi = SmartAPI.get(self.args.id)
                if smartapi.username != self.current_user["login"]:
                    raise HTTPError(403)
                status = smartapi.check()
                smartapi.save()
            except NotFoundError:
                raise HTTPError(404)
            except (ControllerError, AssertionError) as err:
                raise HTTPError(400, reason=str(err))
            else:
                self.finish({"success": True, "details": status})
        else:
            raise HTTPError(400, reason="Missing required parameter: id")

    @github_authenticated
    def post(self):
        if self.args.id:
            try:
                smartapi = SmartAPI.get(self.args.id)
                if smartapi.username != self.current_user["login"]:
                    raise HTTPError(403)
                status = smartapi.check()
                smartapi.save()
            except NotFoundError:
                raise HTTPError(404)
            except (ControllerError, AssertionError) as err:
                raise HTTPError(400, reason=str(err))
            else:
                self.finish({"success": True, "details": status})
        else:
            raise HTTPError(400, reason="Missing required form field: id")


class MetaKGQueryHandler(QueryHandler):
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
            "default_view": {
                "type": str,
                "default": "json",
                "enum": ("json", "cytoscape"),
            },
            "header": {
                "type": bool,
                "default": True
            }
        },
        "GET": {
            **QUERY_KWARGS.get("GET", {}),
            "subject": {"type": list, "max": 1000},
            "object": {"type": list, "max": 1000},
            "node": {"type": list, "max": 1000},  # either subject or object
            "predicate": {"type": list, "max": 1000, "alias": "edge"},
            "size": {"type": int, "max": 5000, "alias": "limit"}, # overwrite size limit for graphml export
            "download": {"type": bool, "default": True},
            "expand": {
                "type": list,
                "max": 6,
                "default": [],
                "enum": ["subject", "object", "predicate", "node", "edge", "all"],
            },
            "default_view": {
                "type": str,
                "default": "json",
                "enum": ("json", "cytoscape"),
            },
            "header": {
                "type": bool,
                "default": True
            }
        },
    }

    def initialize(self, *args, **kwargs):
        super().initialize(*args, **kwargs)
        # change the default query pipeline from self.biothings.pipeline
        self.pipeline = MetaKGQueryPipeline(ns=self.biothings)
        self.biolink_model_toolkit = bmt.Toolkit()

    def get_expanded_values(self, value: Union[str, List[str]]) -> List[str]:
        """return exapnded value list for a given biolink class name"""
        if isinstance(value, str):
            value = [value]
        _out = []
        for v in value:
            try:
                v = self.biolink_model_toolkit.get_descendants(v, reflexive=True, formatted=True)
                v = [x.split(":")[-1] for x in v]  # remove biolink: prefix
            except ValueError:
                v = [v]
            _out.extend(v)
        return _out

    @capture_exceptions
    async def get(self, *args, **kwargs):
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
            value_list = self.get_expanded_values(value_list) if expanded_fields[field] else value_list
            setattr(self.args, field, value_list)

        await super().get(*args, **kwargs)

    def write(self, chunk):
        """
        Overwrite the biothings query handler to add graphml format (&format=graphml)
        * added &download=True to download .graphml file automatically, can disable (&download=False)

        Reshape results for Cytoscape-ready configuration rendering on the front-end. (&format=html)
        """
        try:
            if self.format == "graphml":
                chunk = edges2graphml(chunk, self.request.uri, self.request.protocol, self.request.host, edge_default="directed")
                self.set_header("Content-Type", "text/graphml; charset=utf-8")
                if self.args.download:
                    self.set_header('Content-Disposition', 'attachment; filename="smartapi_metakg.graphml"')

                return super(BaseAPIHandler, self).write(chunk)
            
            if self.format == "html":
                # reformat data
                cdf = CytoscapeDataFormatter(chunk['hits'])
                graph_data = cdf.get_data()
                # setup template
                template_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'templates'))
                loader = Loader(template_path)
                template = loader.load("cytoscape.html")
                # generate global template variable with graph data
                result = template.generate(
                    data=serializer.to_json(graph_data),
                    response=serializer.to_json(chunk),
                    shown=len(chunk['hits']),
                    available=chunk['total'],
                    default_view=serializer.to_json(self.args.default_view),
                    header=serializer.to_json(self.args.header)
                )
                self.set_header("Content-Type", "text/html; charset=utf-8")
                return super(BaseAPIHandler, self).write(result)

        except Exception as exc:
            logger.warning(exc)

        super().write(chunk)
