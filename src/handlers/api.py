
"""
API handler for SmartAPI
Validation /api/validate
Metadata /api/metadata
Suggestion /api/suggestion
"""
import json

from biothings.web.handlers import BaseAPIHandler
from biothings.web.handlers.exceptions import BadRequest
from controller import ControllerError, NotFoundError, SmartAPI
from tornado.web import Finish, HTTPError
from utils.downloader import DownloadError, download_async


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


class APIHandler(BaseHandler):
    """
    Handle CRUD ops for api metadata based on
    openapi v3 or swagger v2
    """

    kwargs = {
        'GET': {
            # 'fields': {'type': list, 'default': []},
            'format': {'type': str, 'default': 'json'},
            'from_': {'type': int, 'default': 0, 'alias': 'from'},
            'size': {'type': int, 'default': 10},
        },
        'PUT': {
            'slug': {'type': str, 'default': None},
        },
        'POST': {
            'url': {'type': str, 'required': True},
            'dryrun': {'type': bool, 'default': False},
        },
    }

    name = "smartapi"

    def get(self, _id=None):
        """
        Get one API or ALL
        """
        if _id is None:
            docs = SmartAPI.get_all(
                from_=self.args.from_,
                size=self.args.size)
            raise Finish([dict(doc) for doc in docs])

        try:
            doc = SmartAPI.get(_id)
        except NotFoundError:
            raise HTTPError(404)
        else:
            self.format = self.args.format
            self.finish(dict(doc))

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
            smartapi.save(file.status == 200)  # TODO TS FIELD REQUIRES TESTING

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
