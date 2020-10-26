
import datetime
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

from biothings.web.api.es.handlers import \
    QueryHandler as BioThingsESQueryHandler
from biothings.web.api.es.handlers.base_handler import BaseESRequestHandler
from tornado.httpclient import HTTPError

# from .es import ESQuery
from web.api.transform import APIMetadata, get_api_metadata_by_url

from utils.slack_notification import send_slack_msg

from web.api.controllers.controller import APIDocController
from web.api.controllers.controller import APIMetadataRegistrationError
from web.api.es import ESQuery


class BaseHandler(BaseESRequestHandler):

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
            return self.return_json(valid)
        else:
            return self.return_json({"valid": False, "error": "The input url does not contain valid API metadata."})

    def get(self):
        url = self.get_argument('url', None)
        if url:
            data = get_api_metadata_by_url(url)
            if data.get('success', None) is False:
                self.return_json(data)
            else:
                self._validate(data)
        else:
            self.return_json(
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
                    return self.return_json({"valid": False, "error": "The input request body does not contain valid API metadata."})
            self._validate(data)
        else:
            self.return_json(
                {"valid": False, "error": "Need to provide data in the request body first."})


class APIHandler(BaseHandler):
    def post(self):
        """
        Add an API doc /api

        Raises:
            HTTPError: invalid format, missing required param

        Returns:
            Success: True if doc created and doc ID
        """
        user = self.get_current_user()
        if not user:
            raise HTTPError(code=401,
                            response={'success': False, 'error': 'Authenticate first with your github account.'})
        else:
            # front-end input options
            possible_options = ['on', '1', 'true']
            # save an API metadata
            overwrite = self.get_argument('overwrite', '').lower()
            overwrite = overwrite in possible_options
            dryrun = self.get_argument('dryrun', '').lower()
            dryrun = dryrun in possible_options
            save_v2 = self.get_argument('save_v2', '').lower()
            save_v2 = save_v2 in possible_options
            url = self.get_argument('url', None)
            if url:
                data = get_api_metadata_by_url(url)
                if data and isinstance(data, dict):
                    if data.get('success', None) is False:
                        self.return_json(data)
                    else:
                        _meta = {
                            "github_username": user['login'],
                            'url': url,
                            'timestamp': datetime.datetime.now().isoformat()
                        }
                        data['_meta'] = _meta

                        try:
                            res = APIDocController.add(api_doc=data,
                                                       overwrite=overwrite,
                                                       dryrun=dryrun,
                                                       user_name=user['login'],
                                                       save_v2=save_v2)
                        except (KeyError, ValueError) as err:
                            raise HTTPError(code=400, response=str(err))
                        except APIMetadataRegistrationError as err:
                            raise APIMetadataRegistrationError(err)
                        except Exception as err:  # unexpected
                            raise HTTPError(500, response=str(err))
                        else:
                            if(res['success'] and not dryrun):
                                self.return_json({'success': True, 'dryrun': False})
                                send_slack_msg(data, res, user['login'])
                            else:
                                # Success but Dryrun
                                self.return_json(res)
                else:
                    raise HTTPError(code=400,
                                    response={'success': False,
                                              'error': 'API metadata is not in a valid format'})

            else:
                raise HTTPError(code=400,
                                response={'success': False,
                                          'error': 'Request is missing a required parameter: url'})


class APIMetaDataHandler(BaseHandler):
    # esq = ESQuery()

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
            self.return_json(res)

    def put(self, _id):
        """
        Must be logged in first
        Updated a slug for a specific API owned by user
        Refresh API metadata for a matched api_name
        OR
        If no slug just refresh document

        Args:
            _id: API id to be changed
        """
        slug_name = self.get_argument('slug', None)
        dryrun = self.get_argument('dryrun', '').lower()
        dryrun = dryrun in ['on', '1', 'true']
        user = self.get_current_user()
        if not user:
            raise HTTPError(code=400,
                            response={'success': False,
                                      'error': 'Must be logged in to perform updates'})
        else:
            if slug_name:
                doc = APIDocController(_id=_id)
                (status, res) = doc.update(_id=_id, user=user, slug_name=slug_name)
            else:
                doc = APIDocController(_id=_id)
                (status, res) = doc.refresh_api(_id=_id, user=user)
            self.set_status(status)
        self.return_json(res)

    def delete(self, _id):
        """
        Delete API metadata
        must be logged in first

        Args:
            _id: API id to be deleted permanently
        """
        user = self.get_current_user()
        slug_name = self.get_argument('slug', '').lower()
        if not user:
            res = {'success': False,
                   'error': 'Authenticate first with your github account.'}
            self.set_status(401)
        # if slug delete
        elif slug_name:
            #prepare doc
            doc = APIDocController(_id=_id)
            (status, res) = doc.delete_slug(
                _id=_id, user=user, slug_name=slug_name)
            self.set_status(status)
        # if api delete
        else:
            #prepare doc
            doc = APIDocController(_id=_id)
            (status, res) = doc.delete(_id=_id, user=user)
            self.set_status(status)
        self.return_json(res)


class ValueSuggestionHandler(BaseHandler):

    def get(self):
        """
        /api/suggestion?field=
        Returns aggregations for any field provided
        Used for tag:count on registry

        Raises:
            HTTPError: required fields not provided
            ValueError: No resutls or bad query
        """
        field = self.get_argument('field', None)
        size = int(self.get_argument('size', 100))

        if not field:
            raise HTTPError(code=400,
                            response={'success': False,
                                      'error': 'Request is missing a required parameter: field'})

        res = APIDocController.get_tags(field=field, size=size)
        if res:
            self.return_json(res)
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
            self.return_json(
                {'success': False, 'error': 'Invalid authentication'})
            return
        data = tornado.escape.json_decode(self.request.body)
        # get repository owner name
        repo_owner = data.get('repository', {}).get(
            'owner', {}).get('name', None)
        if not repo_owner:
            self.set_status(405)
            self.return_json(
                {'success': False, 'error': 'Cannot get repository owner'})
            return
        # get repo name
        repo_name = data.get('repository', {}).get('name', None)
        if not repo_name:
            self.set_status(405)
            self.return_json(
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
