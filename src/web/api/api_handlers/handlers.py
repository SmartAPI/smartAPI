
import hashlib
import hmac
import json
import re

import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import yaml

from biothings.web.handlers import QueryHandler as BioThingsESQueryHandler
from biothings.web.handlers import BaseAPIHandler
from tornado.httpclient import HTTPError

# from .es import ESQuery
from web.api.transform import APIMetadata, get_api_metadata_by_url

from utils.slack_notification import send_slack_msg

from web.api.controllers.controller import APIDocController
from web.api.controllers.controller import APIMetadataRegistrationError
from web.api.es import ESQuery


class BaseHandler(BaseAPIHandler):

    def get_current_user(self):
        user_json = self.get_secure_cookie("user")
        if not user_json:
            return None
        return json.loads(user_json.decode('utf-8'))


class ValidateHandler(BaseHandler):
    def _validate(self, data):
        if data and isinstance(data, dict):
            metadata = APIMetadata(data)
            valid = metadata.validate()
            return self.finish(valid)
        else:
            return self.finish({"valid": False, "error": "The input url does not contain valid API metadata."})

    def get(self):
        url = self.get_argument('url', None)
        if url:
            data = get_api_metadata_by_url(url)
            if data.get('success', None) is False:
                self.finish(data)
            else:
                self._validate(data)
        else:
            self.finish(
                {"valid": False, "error": "Need to provide an input url first."})

    def post(self):
        if self.request.body:
            try:
                data = tornado.escape.json_decode(self.request.body)
            except ValueError:
                try:
                    data = yaml.load(self.request.body, Loader=yaml.SafeLoader)
                except (yaml.scanner.ScannerError,
                        yaml.parser.ParserError):
                    return self.finish({"valid": False, "error": "The input request body does not contain valid API metadata."})
            self._validate(data)
        else:
            self.finish(
                {"valid": False, "error": "Need to provide data in the request body first."})


class APIHandler(BaseHandler):

    kwargs = {
        'POST': {
            'url': {'type': str, 'default': None},
            # optional
            'overwrite': {'type': bool, 'default': False},
            'dryrun': {'type': bool, 'default': False},
            'save_v2': {'type': bool, 'default': False},
        },
    }

    def post(self):
        """
        Add an API metadata doc

        transform.polite_request within transform.get_api_metadata_by_url requests provided url to get openAPI document
        transform.get_api_metadata_by_url will return json or yaml format data
        data is sent to controller where additional metadata will be included then validated and added to index 
        if dryrun requested only steps up to validation will be taken
        else added API doc ID is returned

        Raises:
            HTTPError: 401 unauthorized
            HTTPError: 400 missing parameter
            HTTPError: 422 unidentified entity
            HTTPError: 400 validation error 
        Returns:
            Success: True if doc created and doc ID
        """
        user = self.get_current_user()
        # # front-end input options
        # possible_options = ['on', '1', 'true']

        # overwrite = self.get_argument('overwrite', '').lower()
        # overwrite = overwrite in possible_options
        # dryrun = self.get_argument('dryrun', '').lower()
        # dryrun = dryrun in possible_options
        # save_v2 = self.get_argument('save_v2', '').lower()
        # save_v2 = save_v2 in possible_options
        # url = self.get_argument('url', None)
        print('ARGS', self.args)
        print('ARGS JSON', self.args_json)

        url = self.args.url
        print('url', url)
        if not user:
            raise HTTPError(401)
        if not url:
            raise HTTPError(400)

        data = get_api_metadata_by_url(url)
        data = data.get('metadata', None)

        if not data:
            raise HTTPError(
                code=422,
                response={'success': False, 'error': 'API metadata is not in a valid format'})

        if data.get('success', None) is False:
            self.finish(data)
        else:
            try:
                res = APIDocController.add(
                    api_doc=data,
                    user_name=user['login'],
                    **self.args)

                # res = APIDocController.add(api_doc=data,
                #                            overwrite=overwrite,
                #                            dryrun=dryrun,
                #                            user_name=user['login'],
                #                            save_v2=save_v2,
                #                            url=url)
            except (KeyError, ValueError) as err:
                raise HTTPError(code=400, response=str(err))
            except APIMetadataRegistrationError as err:
                raise HTTPError(400, response=str(err)) from None
            except Exception as err:  # unexpected
                raise HTTPError(500, response=str(err))
            else:
                if('because' not in res):
                    # Successful Save
                    self.finish({'success': True, 'details': res})
                    send_slack_msg(data, res, user['login'])
                else:
                    # Any Errors/Tests
                    self.finish({"success": False, 'details': res})



class APIMetaDataHandler(BaseHandler):

    kwargs = {
        'GET': {
            'fields': {'type': str, 'default': None},
            'format': {'type': str, 'default': 'json'},
            'raw': {'type': bool, 'default': False},
            'meta': {'type': bool, 'default': False},
            'from': {'type': int, 'default': 0},
        },
        'PUT': {
            'slug': {'type': str, 'default': ''},
            'dryrun': {'type': str, 'default': ''}
        },
        'DELETE': {
            'slug': {'type': str, 'default': ''}
        },
    }

    def get(self, api_name):
        """
        Get API doc by name
        if api_name is "all", return a list of all APIs
        size capped to 100 for now by get_api method below.

        Args:
            api_name (str): name of API doc requested

        Returns:
            JSON or YAML of doc requested
        """
        fields = self.get_argument('fields', None)
        out_format = self.get_argument('format', 'json').lower()
        return_raw = self.get_argument('raw', False)
        with_meta = self.get_argument('meta', False)
        size = self.get_argument('size', None)
        from_ = self.get_argument('from', 0)
        try:
            size = int(size)
        except (TypeError, ValueError):
            size = None
        try:
            from_ = int(from_)
        except (TypeError, ValueError):
            from_ = 0
        if fields:
            fields = fields.split(',')

        res = APIDocController.get_api(api_name=api_name, fields=fields, with_meta=with_meta, return_raw=return_raw, size=size, from_=from_)

        if out_format == 'yaml':
            self.return_yaml(res)
        else:
            self.finish(res)

    def put(self, _id):
        """
        Update a slug for a specific API
        OR
        If no slug just refresh document using url

        Args:
            _id: API id to be updated
        """
        slug_name = self.get_argument('slug', None)
        dryrun = self.get_argument('dryrun', '').lower()
        dryrun = dryrun in ['on', '1', 'true']
        user = self.get_current_user()
        if not user:
            raise HTTPError(code=400, response={'success': False, 'error': 'Must be logged in to perform updates'})
        else:
            if slug_name:
                doc = APIDocController(_id=_id)
                res = doc.update(_id=_id, user=user, slug_name=slug_name)
            else:
                doc = APIDocController(_id=_id)
                res = doc.refresh_api(_id=_id, user=user)
        if 'because' in res:
            self.finish({'success': False, 'details': res})
        else:
            self.finish({'success': True, 'details': res})

    def delete(self, _id):
        """
        Delete API or slug only if provided

        Args:
            _id: API id to be deleted permanently
            slug: API slug
        """
        user = self.get_current_user()
        slug_name = self.get_argument('slug', '').lower()
        if not user:
            res = {'success': False,
                   'error': 'Authenticate first with your github account.'}
            self.set_status(401)
        elif slug_name:
            doc = APIDocController(_id=_id)
            res = doc.delete_slug(_id=_id, user=user, slug_name=slug_name)
        else:
            doc = APIDocController(_id=_id)
            res = doc.delete(_id=_id, user=user)

        if 'because' in res:
            self.finish({'success': False, 'details': res})
        else:
            self.finish({'success': True, 'details': res})


class ValueSuggestionHandler(BaseHandler):

    def get(self):
        """
        /api/suggestion?field=
        Returns aggregations for any field provided
        Used for tag:count on registry

        Raises:
            HTTPError: required fields not provided
            ValueError: No results or bad query
        """
        field = self.get_argument('field', None)
        size = int(self.get_argument('size', 100))

        if not field:
            raise HTTPError(code=400,
                            response={'success': False,
                                      'error': 'Request is missing a required parameter: field'})

        res = APIDocController.get_tags(field=field, size=size)
        if res:
            self.finish(res)
        else:
            raise ValueError(f'Suggestion not possible for {field}')


class GitWebhookHandler(BaseHandler):
    esq = ESQuery()

    def post(self):
        # do message authentication
        digest_obj = hmac.new(key=self.web_settings.API_KEY.encode(
        ), msg=self.request.body, digestmod=hashlib.sha1)
        if not hmac.compare_digest('sha1=' + digest_obj.hexdigest(), self.request.headers.get('X-Hub-Signature', '')):
            self.set_status(405)
            self.finish(
                {'success': False, 'error': 'Invalid authentication'})
            return
        data = tornado.escape.json_decode(self.request.body)
        # get repository owner name
        repo_owner = data.get('repository', {}).get(
            'owner', {}).get('name', None)
        if not repo_owner:
            self.set_status(405)
            self.finish(
                {'success': False, 'error': 'Cannot get repository owner'})
            return
        # get repo name
        repo_name = data.get('repository', {}).get('name', None)
        if not repo_name:
            self.set_status(405)
            self.finish(
                {'success': False, 'error': 'Cannot get repository name'})
            return
        # find all modified files in all commits
        modified_files = set()
        for commit_obj in data.get('commits', []):
            for fi in commit_obj.get('added', []):
                modified_files.add(fi)
            for fi in commit_obj.get('modified', []):
                modified_files.add(fi)
        # build query
        _query = {"query": {"bool": {"should": [
            {"regexp": {"_meta.url.raw": {"value": '.*{owner}/{repo}/.*/{fi}'.format(owner=re.escape(repo_owner), repo=re.escape(repo_name), fi=re.escape(fi)),
                                          "max_determinized_states": 200000}}} for fi in modified_files]}}}
        # s = Search()
        # s.query = Q('bool', should=[Q('regexp', _meta__url__raw='.*{owner}/{repo}/.*/{fi}'
        # .format(owner=re.escape(repo_owner), repo=re.escape(repo_name), fi=re.escape(fi))),
        #                             Q()])
        # res = s.execute().to_dict()

        # get list of ids that need to be refreshed
        ids_refresh = [x['_id'] for x in self.esq.fetch_all(query=_query)]
        # if there are any ids to refresh, do it
        if ids_refresh:
            self.esq.refresh_all(id_list=ids_refresh, dryrun=False)


APP_LIST = [
    (r'/?', APIHandler),
    (r'/query/?', BioThingsESQueryHandler),
    (r'/validate/?', ValidateHandler),
    (r'/metadata/(.+)/?', APIMetaDataHandler),
    (r'/suggestion/?', ValueSuggestionHandler),
    (r'/webhook_payload/?', GitWebhookHandler),
]
