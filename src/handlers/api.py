
import json

import yaml
from biothings.web.handlers import BaseAPIHandler
from biothings.web.handlers.exceptions import BadRequest
from tornado.httpclient import HTTPError

from controller import RegistryError, SmartAPI
from utils.downloader import SchemaDownloader, DownloadError
from utils.notify import send_slack_msg


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

    def get_current_user(self):
        user_json = self.get_secure_cookie("user")
        if not user_json:
            return None
        return json.loads(user_json.decode('utf-8'))

class ValidateHandler(BaseHandler):

    kwargs = {
        'POST': {
            'url': {'type': str, 'default': None},
        },
    }
    name = "validator"

    def post(self):

        url = self.get_body_argument('url', None)
        data = None

        if url:
            try:
                data = SchemaDownloader.download(url)
            except RegistryError as err:
                raise BadRequest(details=str(err))

        elif self.request.headers.get('Content-Type', '').startswith('application/json'):
            try:
                data = self.args_json
            except json.JSONDecodeError:
                raise BadRequest(details="Invalid JSON body")

        elif self.request.headers.get('Content-Type', '').startswith('application/yaml'):
            try:
                data = yaml.load(self.request.body, Loader=yaml.SafeLoader)
            except (yaml.scanner.ScannerError, yaml.parser.ParserError):
                raise BadRequest(details="The input request body does not contain valid API metadata")
        else:
            raise BadRequest(details="Need to provide data in the request body first")

        try:
            valid = SmartAPI.validate(data)
        except RegistryError as err:
            raise BadRequest(details=str(err))
        else:
            self.finish(valid)


class APIHandler(BaseHandler):

    kwargs = {
        'GET': {
            'fields': {'type': list, 'default': []},
            'format': {'type': str, 'default': 'json'},
            '_from': {'type': int, 'default': 0},
            'size': {'type': int, 'default': 10},
        },
        'PUT': {
            'slug': {'type': str, 'default': None},
        },
        'POST': {
            'url': {'type': str, 'default': None, 'required': True},
            'overwrite': {'type': bool, 'default': False},
            'dryrun': {'type': bool, 'default': False},
            'save_v2': {'type': bool, 'default': False},
        },
    }

    name = "api_handler"

    def get(self, _id=None):
        """
        Get one API or ALL
        """
        if _id is None:
            res = SmartAPI.get_all(
                fields=self.args.fields,
                from_=self.args._from,
                size=self.args.size)
        else:
            if not SmartAPI.exists(_id):
                raise HTTPError(404, response='API does not exist')

            res = SmartAPI.get_api_by_id(_id)
            # needed for get_all?
            res = dict(res)

        self.format = self.args.format
        self.finish(res)

    @github_authenticated
    def post(self):
        """
        Add an API metadata doc
        """
        user = self.current_user

        if SmartAPI.exists(self.args.url, "_meta.url"):
            if not self.args.overwrite:
                raise RegistryError('API exists')

        try:
            file = SchemaDownloader.download(self.args.url)
        except RegistryError as err:
            raise BadRequest(details=str(err))

        try:
            doc = SmartAPI.from_dict(file.data)
            doc.username = user['login']
            doc.url = self.args.url
            doc.etag = file.etag
            doc.validate()
        except RegistryError as err:
            raise BadRequest(details=str(err))

        if self.args.dryrun:
            self.finish({'success': True, 'details': f"[Dryrun] Valid {doc.version} Metadata"})
            return
        try:
            res = doc.save()
        except RegistryError as err:
            raise BadRequest(details=str(err))
        else:
            self.finish({'success': True, 'details': res})
            send_slack_msg(file.data, res, user['login'])

    @github_authenticated
    def put(self, _id):
        """
        Update registered slug or refresh by url
        """
        if not SmartAPI.exists(_id):
            raise HTTPError(404, response='API does not exist')

        if self.args.slug is None:
            try:
                doc = SmartAPI.get_api_by_id(_id)
                res = doc.refresh()
            except (RegistryError, DownloadError) as err:
                raise BadRequest(details=str(err))
        else:
            try:
                doc = SmartAPI.get_api_by_id(_id)
                doc.slug = self.args.slug
                res = doc.update_slug()
            except RegistryError as err:
                raise BadRequest(details=str(err))

        self.finish({'success': True, 'details': res})

    @github_authenticated
    def delete(self, _id):
        """
        Delete API
        """
        if not SmartAPI.exists(_id):
            raise HTTPError(404, response='API does not exist')
        try:
            doc = SmartAPI.get_api_by_id(_id)
            res = doc.delete()
        except RegistryError as err:
            raise BadRequest(details=str(err))

        self.finish({'success': True, 'details': res})


class ValueSuggestionHandler(BaseHandler):

    kwargs = {
        'GET': {
            'field': {'type': str, 'default': None, 'required': True},
            'size': {'type': int, 'default': 100},
        },
    }

    name = 'value_suggestion'

    def get(self):
        """
        /api/suggestion?field=
        Returns aggregations for any field provided
        Used for tag:count on registry
        """
        res = SmartAPI.get_tags(self.args.field, self.args.size)
        self.finish(res)
