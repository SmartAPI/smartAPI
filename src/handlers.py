
import json
import logging

import certifi
# import torngithub
from biothings.web.handlers import BaseAPIHandler, BiothingHandler
# from torngithub import json_encode
from tornado.escape import to_basestring
from tornado.httpclient import AsyncHTTPClient
from tornado.httputil import url_concat
from tornado.web import Finish, HTTPError

from controller import ControllerError, NotFoundError, SmartAPI
from utils.downloader import DownloadError, download_async
from utils.notification import SlackNewAPIMessage, SlackNewTranslatorAPIMessage


def json_encode(value):
    return json.dumps(value).replace("</", "<\\/")


def json_decode(value):
    return json.loads(to_basestring(value))


def github_authenticated(func):
    """
    RegistryHandler Decorator
    """

    def _(self, *args, **kwargs):

        if not self.current_user:
            self.send_error(
                message='You must log in first.',
                status_code=401)
            return
        return func(self, *args, **kwargs)

    return _


class BaseHandler(BaseAPIHandler):
    """
    Base SmartAPI Handler
    """
    cache = 0

    async def prepare(self):

        super().prepare()

        # Additionally support GitHub Token Login
        # Mainly for debug and admin purposes

        if 'Authorization' in self.request.headers:
            if self.request.headers['Authorization'].startswith('Bearer '):
                token = self.request.headers['Authorization'].split(' ', 1)[1]
                http_client = AsyncHTTPClient()
                try:
                    response = await http_client.fetch(
                        "https://api.github.com/user", request_timeout=10,
                        headers={'Authorization': 'token ' + token}, ca_certs=certifi.where())
                    user = json.loads(response.body)
                except Exception as e:  # TODO
                    logging.warning(e)
                else:
                    if 'login' in user:
                        logging.info('logged in user from github token: %s', user)
                        self.set_secure_cookie("user", json_encode(user))
                        self.current_user = user

    def get_current_user(self):
        user_json = self.get_secure_cookie("user")
        if not user_json:
            return None
        return json.loads(user_json.decode('utf-8'))

        # DEBUG USAGE
        # return {"login": "tester"}


class UserInfoHandler(BaseHandler):
    def get(self):
        current_user = self.get_current_user() or {}
        for key in ['access_token', 'id']:
            if key in current_user:
                del current_user[key]
        self.finish(current_user)


class LoginHandler(BaseHandler):
    def get(self):
        self.redirect(self.get_argument("next", "/"))


class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("user")
        self.redirect(self.get_argument("next", "/"))


# class GithubLoginHandler(BaseHandler, torngithub.GithubMixin):

#     GITHUB_SCOPE = ""
#     GITHUB_CALLBACK_PATH = "/oauth"

#     @tornado.gen.coroutine
#     def get(self):
#         # we can append next to the redirect uri, so the user gets the
#         # correct URL on login
#         redirect_uri = url_concat(self.request.protocol +
#                                   "://" + self.request.host +
#                                   self.GITHUB_CALLBACK_PATH,
#                                   {"next": self.get_argument('next', '/')})

#         # if we have a code, we have been authorized so we can log in
#         if self.get_argument("code", False):
#             user = yield self.get_authenticated_user(
#                 redirect_uri=redirect_uri,
#                 client_id=self.web_settings.GITHUB_CLIENT_ID,
#                 client_secret=self.web_settings.GITHUB_CLIENT_SECRET,
#                 code=self.get_argument("code"),
#                 callback=lambda: None
#             )
#             if user:
#                 logging.info('logged in user from github: %s', str(user))
#                 self.set_secure_cookie("user", json_encode(user))
#             else:
#                 self.clear_cookie("user")
#             self.redirect(self.get_argument("next", "/"))
#             return

#         # otherwise we need to request an authorization code
#         yield self.authorize_redirect(
#             redirect_uri=redirect_uri,
#             client_id=self.web_settings.GITHUB_CLIENT_ID,
#             extra_params={"scope": self.GITHUB_SCOPE, "foo": 1}
#         )


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
        "GET": {
            "url": {"type": str, "location": "query", "required": True}
        },
        "POST": {
            "url": {"type": str, "location": "form"}
        }
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
            self.finish({
                'success': True,
                'details': f'valid SmartAPI ({smartapi.version}) metadata.'
            })


class SmartAPIHandler(BaseHandler, BiothingHandler):

    kwargs = {
        '*': BiothingHandler.kwargs['*'],
        'PUT': {
            'slug': {'type': str, 'default': None},
        },
        'POST': {
            'url': {'type': str, 'required': True},
            'dryrun': {'type': bool, 'default': False},
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
            raise Finish({
                'success': True,
                'details': f"[Dryrun] Valid {smartapi.version} Metadata"
            })

        try:
            smartapi.username = self.current_user['login']
            smartapi.refresh(file)  # populate webdoc meta
            _id = smartapi.save()
        except ControllerError as err:
            raise HTTPError(400, reason=str(err)) from err
        else:
            self.finish({
                'success': True,
                '_id': _id
            })
            await self._notify(smartapi)

    async def _notify(self, smartapi):

        if self.settings.get('debug'):
            return

        client = AsyncHTTPClient()
        kwargs = {
            "_id": smartapi._id,
            "name": dict(smartapi).get('info', {}).get('title', '<Notitle>'),
            "description": dict(smartapi).get('info', {}).get('description', '')[:120] + '...',
            "username": smartapi.username
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
                                slack["webhook"], method='POST',
                                headers={'content-type': 'application/json'},
                                body=json.dumps(SlackNewTranslatorAPIMessage(**kwargs).compose()),
                            )
                            logging.info(res.code)
                            logging.info(res.body)

                    # elif slack["tags"] == <other>:
                    #   pass

                else:  # typical case
                    res = await client.fetch(
                        slack["webhook"], method='POST',
                        headers={'content-type': 'application/json'},
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

        if smartapi.username != self.current_user['login']:
            raise HTTPError(403)

        if self.args.slug is not None:

            if self.args.slug in {'api'}:  # reserved
                raise HTTPError(400, reason='slug is reserved')

            try:  # update slug
                smartapi.slug = self.args.slug or None
                smartapi.save()

            except (ControllerError, ValueError) as err:
                raise HTTPError(400, reason=str(err)) from err

            self.finish({'success': True})

        else:  # refresh
            file = await download_async(smartapi.url, raise_error=False)
            code = smartapi.refresh(file)
            smartapi.save()

            try:
                status = smartapi.webdoc.STATUS(code)
                status = status.name.lower()
            except ValueError:
                status = 'nofile'  # keep the original copy

            self.finish({
                'success': code in (200, 299),
                'status': status,
                'code': code
            })

    @github_authenticated
    def delete(self, _id):
        """
        Delete API
        """

        try:
            smartapi = SmartAPI.get(_id)
        except NotFoundError:
            raise HTTPError(404)

        if smartapi.username != self.current_user['login']:
            raise HTTPError(403)

        try:
            _id = smartapi.delete()
        except ControllerError as err:
            raise HTTPError(400, reason=str(err)) from err

        self.finish({'success': True, '_id': _id})


class ValueSuggestionHandler(BaseHandler):
    """
    Handle field aggregation for UI suggestions
    """

    kwargs = {
        'GET': {
            'field': {'type': str, 'required': True}
        },
    }

    name = 'value_suggestion'

    def get(self):
        """
        /api/suggestion?field=
        Returns aggregations for any field provided
        Used for tag:count on registry
        """
        res = SmartAPI.get_tags(self.args.field)
        self.finish(res)
