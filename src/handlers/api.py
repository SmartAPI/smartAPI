"""
API handler for SmartAPI
Validation /api/validate
Metadata /api/metadata
Suggestion /api/suggestion
"""
import json

import yaml
from biothings.web.handlers import BaseAPIHandler
from biothings.web.handlers.exceptions import BadRequest
from tornado.web import HTTPError

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
    """
    Base SmartAPI Handler
    """

    def get_current_user(self):
        user_json = self.get_secure_cookie("user")
        if not user_json:
            return None
        return json.loads(user_json.decode('utf-8'))

class ValidateHandler(BaseHandler):
    """
    Validate api metadata based on
    openapi v3 or swagger v2
    accepts url or content body
    """

    kwargs = {
        'POST': {
            'url': {'type': str, 'default': None},
        },
    }
    name = "validator"

    def post(self): # pylint: disable=arguments-differ

        if 'url' in self.request.body_arguments:
            try:
                url = self.get_body_argument('url', None)
                file = SchemaDownloader.download(url)
                data = file.data
            except RegistryError as err:
                raise BadRequest(details=str(err)) from err

        elif self.request.headers.get('Content-Type', '').startswith('application/json'):
            try:
                data = self.args_json
            except json.JSONDecodeError as err:
                raise BadRequest(details="Invalid JSON body") from err

        elif self.request.headers.get('Content-Type', '').startswith('application/yaml'):
            try:
                data = yaml.load(self.request.body, Loader=yaml.SafeLoader)
            except (yaml.scanner.ScannerError, yaml.parser.ParserError) as err:
                raise BadRequest(details="Body does not contain valid API metadata") from err
        else:
            raise BadRequest(details="Need to provide data in the request body first")

        try:
            doc = SmartAPI.from_dict(data)
            doc.validate()

        except RegistryError as err:
            raise BadRequest(details=str(err)) from err
        else:
            self.finish({'success': True, 'details': f'Valid [{doc.version}] metadata'})


class APIHandler(BaseHandler):

    """
    Handle CRUD ops for api metadata based on
    openapi v3 or swagger v2
    """

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
            'url': {'type': str, 'required': True},
            'overwrite': {'type': bool, 'default': False},
            'dryrun': {'type': bool, 'default': False},
        },
    }

    name = "api_handler"

    def get(self, _id=None):  # pylint: disable=arguments-differ
        """
        Get one API or ALL
        """
        if _id is None:
            res = SmartAPI.get_all(
                fields=self.args.fields,
                from_=self.args._from,  # pylint: disable=protected-access
                size=self.args.size)
        else:
            if not SmartAPI.exists(_id):
                raise HTTPError(404, reason='API does not exist')

            res = SmartAPI.get_api_by_id(_id)

        self.format = self.args.format
        self.finish(dict(res))

    @github_authenticated
    def post(self):  # pylint: disable=arguments-differ
        """
        Add an API metadata doc
        """
        user = self.current_user

        existing_doc = SmartAPI.exists(self.args.url, "_meta.url")

        if existing_doc:
            if user['login'] != existing_doc.username:
                raise HTTPError(401)
            if not self.args.overwrite:
                raise BadRequest(details='API exists')

        try:
            file = SchemaDownloader.download(self.args.url)
        except RegistryError as err:
            raise BadRequest(details=str(err)) from err

        try:
            doc = SmartAPI.from_dict(file.data)
            doc.username = user['login']
            doc.url = self.args.url
            doc.etag = file.etag
            doc.validate()
        except RegistryError as err:
            raise BadRequest(details=str(err)) from err

        if self.args.dryrun:
            self.finish({'success': True, 'details': f"[Dryrun] Valid {doc.version} Metadata"})
            return
        try:
            res = doc.save()
        except RegistryError as err:
            raise BadRequest(details=str(err)) from err
        else:
            self.finish({'success': True, 'details': res})
            send_slack_msg(file.data, res, user['login'])

    @github_authenticated
    def put(self, _id):  # pylint: disable=arguments-differ
        """
        Update registered slug or refresh by url
        """
        user = self.current_user

        if not SmartAPI.exists(_id):
            raise HTTPError(404, reason='API does not exist')

        existing_doc = SmartAPI.get_api_by_id(_id)
        if user['login'] != existing_doc.username:
            self.send_error(
                    message='Unauthorized [update] not allowed', status_code=401)

        if self.args.slug:
            try:
                doc = SmartAPI.get_api_by_id(_id)
                doc.slug = self.args.slug
                res = doc.save()
            except RegistryError as err:
                raise BadRequest(details=str(err)) from err
        else:
            # Refresh doc assumed if no slug provided
            try:
                doc = SmartAPI.get_api_by_id(_id)
                res = doc.refresh()
            except (RegistryError, DownloadError) as err:
                raise BadRequest(details=str(err)) from err

        self.finish({'success': True, 'details': res})

    @github_authenticated
    def delete(self, _id):  # pylint: disable=arguments-differ
        """
        Delete API
        """
        user = self.current_user

        if not SmartAPI.exists(_id):
            raise HTTPError(404, reason='API does not exist')

        doc = SmartAPI.get_api_by_id(_id)
        if user['login'] != doc.username:
            raise HTTPError(401)

        try:
            res = doc.delete()
        except RegistryError as err:
            raise BadRequest(details=str(err)) from err

        self.finish({'success': True, 'details': res})


class ValueSuggestionHandler(BaseHandler):
    """
    Handle field aggregation for UI suggestions
    """

    kwargs = {
        'GET': {
            'field': {'type': str, 'required': True},
            'size': {'type': int, 'default': 10},
        },
    }

    name = 'value_suggestion'

    def get(self):  # pylint: disable=arguments-differ
        """
        /api/suggestion?field=
        Returns aggregations for any field provided
        Used for tag:count on registry
        """
        res = SmartAPI.get_tags(self.args.field, self.args.size)
        self.finish(res)


class APIStatusHandler(BaseHandler):
    """
    Handle api and url status
    """
    name = 'status_handler'

    def get(self, _id):  # pylint: disable=arguments-differ
        """
        /api/status/<id>
        returns collected routine uptime and url status
        """
        if not SmartAPI.exists(_id):
            raise HTTPError(404, reason='API does not exist')

        doc = SmartAPI.get_api_by_id(_id)
        try:
            res = doc.get_status()
        except RegistryError as err:
            raise BadRequest(details=str(err)) from err
        else:
            self.finish(res)
