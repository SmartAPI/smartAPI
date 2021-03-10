
"""
API handler for SmartAPI
Validation /api/validate
Metadata /api/metadata
Suggestion /api/suggestion
"""
import json
import logging
from collections import OrderedDict

import certifi
from biothings.web.handlers import BaseAPIHandler, BiothingHandler
from biothings.web.handlers.exceptions import BadRequest, EndRequest
from controller import ControllerError, NotFoundError, SmartAPI
from tornado.httpclient import AsyncHTTPClient
from tornado.web import Finish, HTTPError
from torngithub import json_encode
from utils.downloader import DownloadError, download_async
from utils.notification import SlackNewAPIMessage, SlackNewTranslatorAPIMessage


def github_authenticated(func):
    '''
    RegistryHandler Decorator
    '''

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


class ValidateHandler(BaseHandler):
    """
    Validate Swagger/OpenAPI document.
    Accepts URL in form data, JSON/YAML body.
    """

    name = "validator"
    kwargs = {
        "POST": {
            "url": {"type": str, "location": "form"}
        }
    }

    async def post(self):

        if self.args.url:

            try:
                file = await download_async(self.args.url)
            except DownloadError as err:
                raise BadRequest(details=str(err))
            else:  # other file info irrelevent for validation
                raw = file.raw

        else:  # then treat the request body as raw
            raw = self.request.body

        try:
            smartapi = SmartAPI(SmartAPI.VALIDATION_ONLY)
            smartapi.raw = raw
            smartapi.validate()

        except (ControllerError, AssertionError) as err:
            raise BadRequest(details=str(err))
        else:
            self.finish({
                'success': True,
                'details': f'Valid {smartapi.version} metadata.'
            })


class SmartAPIReadOnlyHandler(BiothingHandler):

    def pre_query_builder_hook(self, options):
        options = super().pre_query_builder_hook(options)

        if options.esqb.q:
            # id query cannot perform pagination
            options.esqb.pop('size', None)
            options.esqb.pop('from', None)
        else:
            # perform get_all if no particular id is given
            options.esqb.q = options.esqb.q or '__all__'
            options.esqb.scopes = None  # not a match query

        return options

    def pre_transform_hook(self, options, res):

        # raw == 1 is reserved for adding underscore fields
        if options.control.raw == 2:
            raise Finish(res)

        return res

    def pre_finish_hook(self, options, res):

        if isinstance(res, dict):

            # get all
            # --------------
            if options.esqb.q == '__all__':
                return self.pre_finish_hook(options, res['hits'])

            # get one
            # --------------
            if not res.get('hits'):
                template = self.web_settings.ID_NOT_FOUND_TEMPLATE
                reason = template.format(bid=options.esqb.q)
                raise EndRequest(404, reason=reason)

            res = res['hits'][0]
            res.pop('_score', None)
            res = OrderedDict(res)

        elif isinstance(res, list):
            for hit in res:
                hit.pop('_score', None)
            res = [OrderedDict(hit) for hit in res]

        return res


class SmartAPIHandler(BaseHandler, SmartAPIReadOnlyHandler):

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

    async def prepare(self):
        await super().prepare()

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
            raise BadRequest(details=str(err)) from err

        try:
            smartapi = SmartAPI(self.args.url)
            smartapi.raw = file.raw
            smartapi.validate()
        except (ControllerError, AssertionError) as err:
            raise BadRequest(details=str(err)) from err

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
            raise BadRequest(details=str(err)) from err
        else:
            self.finish({
                'success': True,
                '_id': _id
            })
            await self._notify(smartapi)

    async def _notify(self, smartapi):
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

            try:  # update slug
                smartapi.slug = self.args.slug or None
                smartapi.save()

            except (ControllerError, ValueError) as err:
                raise BadRequest(details=str(err)) from err

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
            raise BadRequest(details=str(err)) from err

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
