import datetime
import hashlib
import hmac
import json
import re
from collections import OrderedDict

import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import yaml

from biothings.web.api.es.handlers import \
    QueryHandler as BioThingsESQueryHandler
from biothings.web.api.es.handlers.base_handler import BaseESRequestHandler

from .es import ESQuery
from .transform import APIMetadata, get_api_metadata_by_url

from utils.slack_notification import send_slack_msg

from .controllers.controller import APIDocController

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
        # check if a logged in user
        user = self.get_current_user()
        if not user:
            res = {'success': False,
                   'error': 'Authenticate first with your github account.'}
            self.set_status(401)
            self.return_json(res)
        else:
            # save an API metadata
            overwrite = self.get_argument('overwrite', '').lower()
            overwrite = overwrite in ['1', 'true']
            dryrun = self.get_argument('dryrun', '').lower()
            dryrun = dryrun in ['on', '1', 'true']
            save_v2 = self.get_argument('save_v2', '').lower()
            save_v2 = save_v2 in ['1', 'true']
            url = self.get_argument('url', None)
            if url:
                data = get_api_metadata_by_url(url)
                # try:
                #     data = tornado.escape.json_decode(data)
                # except ValueError:
                #     data = None
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

                        res = APIDocController.add(api_doc=data, overwrite=overwrite, dryrun=dryrun, user_name=user['login'], save_v2=save_v2)
                        # esq = ESQuery()
                        # res = esq.save_api(
                        #     data, overwrite=overwrite, dryrun=dryrun, user_name=user['login'], save_v2=save_v2)
                        ## send notification to slack 
                        if(res):
                            self.return_json({'success': True})
                            send_slack_msg(data, res, user['login']) 
                        else:     
                            self.return_json({'success': False, 'error': 'Something went wrong.'})
                else:
                    self.return_json(
                        {'success': False, 'error': 'Invalid input data.'})

            else:
                self.return_json(
                    {'success': False, 'error': 'missing required parameter.'})


class APIMetaDataHandler(BaseHandler):
    esq = ESQuery()

    def get(self, api_name):
        '''return API metadata for a matched api_name,
           if api_name is "all", return a list of all APIs
        '''
        fields = self.get_argument('fields', None)
        out_format = self.get_argument('format', 'json').lower()
        return_raw = self.get_argument('raw', False)
        with_meta = self.get_argument('meta', False)
        size = self.get_argument('size', None)
        from_ = self.get_argument('from', 0)
        try:
            # size capped to 100 for now by get_api method below.
            size = int(size)
        except (TypeError, ValueError):
            size = None
        try:
            from_ = int(from_)
        except (TypeError, ValueError):
            from_ = 0
        if fields:
            fields = fields.split(',')
        res = APIDocController.get_all(api_name)
        # res = self.esq.get_api(api_name, fields=fields, with_meta=with_meta,
        #                        return_raw=return_raw, size=size, from_=from_)
        if out_format == 'yaml':
            self.return_yaml(res)
        else:
            self.return_json(res)

    def put(self, api_name):
        ''' refresh API metadata for a matched api_name,
            checks to see if current user matches the creating user.'''
        slug_name = self.get_argument('slug', None)
        dryrun = self.get_argument('dryrun', '').lower()
        dryrun = dryrun in ['on', '1', 'true']
        # must be logged in first
        user = self.get_current_user()
        if not user:
            res = {'success': False,
                   'error': 'Authenticate first with your github account.'}
            self.set_status(401)
        else:
            if slug_name:
                (status, res) = self.esq.set_slug_name(
                    _id=api_name, user=user, slug_name=slug_name)
            else:
                (status, res) = self.esq.refresh_one_api(
                    _id=api_name, user=user, dryrun=dryrun)
            self.set_status(status)
        self.return_json(res)

    def delete(self, api_name):
        '''delete API metadata for a matched api_name,
           checks to see if current user matches the creating user.'''
        # must be logged in first
        user = self.get_current_user()
        slug_name = self.get_argument('slug', '').lower()
        if not user:
            res = {'success': False,
                   'error': 'Authenticate first with your github account.'}
            self.set_status(401)
        elif slug_name:
            (status, res) = self.esq.delete_slug(
                _id=api_name, user=user, slug_name=slug_name)
            self.set_status(status)
        else:
            (status, res) = self.esq.archive_api(api_name, user)
            self.set_status(status)
        self.return_json(res)


class ValueSuggestionHandler(BaseHandler):

    def get(self):
        '''
            Updated to use ES-DSL
        '''
        field = self.get_argument('field', None)
        try:
            size = int(self.get_argument('size', 100))
        except:
            size = 100
        if field:
            docs = APIDocController()
            res = docs.get_tags(field= field, size= size)
        else:
            res = {'error': 'missing required "field" parameter'}
        self.return_json(res)

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
