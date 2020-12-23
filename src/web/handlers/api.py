
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
from biothings.web.handlers.exceptions import BadRequest
from tornado.httpclient import HTTPError

from utils.slack_notification import send_slack_msg

from ..api.controller import (APIMetadata, ValidationError, APIDocController, APIMetadataRegistrationError,
                              get_api_metadata_by_url, APIRequestError, SlugRegistrationError)
from utils.data import SmartAPIData


class BaseHandler(BaseAPIHandler):

    def get_current_user(self):
        user_json = self.get_secure_cookie("user")
        if not user_json:
            return None
        return json.loads(user_json.decode('utf-8'))


class ValidateHandler(BaseHandler):

    kwargs = {
        'GET': {
            'url': {'type': str, 'default': None},
        },
    }
    name = "validator"

    def get(self):
        if not self.args.url:
            raise HTTPError(400, response='URL is required')

        data = get_api_metadata_by_url(self.args.url)

        try:
            metadata = APIMetadata(data)
            valid = metadata.validate()
        except (ValidationError, APIRequestError) as err:
            raise BadRequest(details=str(err))
        else:
            self.finish(valid)

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
        'GET': {
            'fields': {'type': list, 'default': None},
            'format': {'type': str, 'default': 'json'},
            'raw': {'type': bool, 'default': False},
            'meta': {'type': bool, 'default': False},
            '_from': {'type': int, 'default': 0},
            'size': {'type': int, 'default': 0},
        },
        'PUT': {
            'slug': {'type': str, 'default': ''},
            'refresh': {'type': bool, 'default': False},
        },
        'POST': {
            'url': {'type': str, 'default': None, 'required': True},
            'overwrite': {'type': bool, 'default': False},
            'dryrun': {'type': bool, 'default': False},
            'save_v2': {'type': bool, 'default': False},
        },
    }

    name = "api_handler"

    def get(self, api_name):
        """
        Get one API by ID or all

        Args:
            api_name (str): name of API doc requested

        Returns:
            JSON or YAML of doc requested
        """
        if api_name == 'all':
            res = APIDocController.get_all(fields=self.args.fields,
                                           from_=self.args._from)
        else:
            res = APIDocController.get_api(api_name=api_name,
                                           fields=self.args.fields,
                                           with_meta=self.args.meta,
                                           return_raw=self.args.raw,
                                           size=self.args.size,
                                           from_=self.args._from)

        self.format = self.args.out_format
        self.finish(res)

    def post(self):
        """
        Add an API metadata doc
        """
        user = self.current_user
        url = self.args.url
        if not user:
            raise HTTPError(401, response='Login required')
        if not url:
            raise HTTPError(400, response='URL is required')

        data = None
        try:
            data = get_api_metadata_by_url(url)
        except APIRequestError as err:
            raise BadRequest(details=str(err))
        except Exception as err:
            raise HTTPError(500, response=str(err))

        try:
            res = APIDocController.add(
                api_doc=data,
                user_name=user['login'],
                **self.args)

        except (APIMetadataRegistrationError, ValidationError, APIRequestError) as err:
            raise BadRequest(details=str(err))
        except Exception as err:
            raise HTTPError(500, response=str(err))
        else:
            self.finish({'success': True, 'details': res})
            send_slack_msg(data, res, user['login'])

    def put(self, _id):
        """
        Update a slug
        OR
        refresh document using url

        Args:
            slug: update with value or empty if 'deleting'
            refresh: determine operation / update doc by url
        """
        if not self.current_user:
            raise HTTPError(401, response='Login required')

        doc = APIDocController(_id=_id)

        if refresh is False:
            try:
                res = doc.update_slug(_id=_id, user=self.current_user, slug_name=self.args.slug)
            except SlugRegistrationError as err:
                raise BadRequest(details=str(err))
            except Exception as err:
                raise HTTPError(500, response=str(err))
        else:
            try:
                res = doc.refresh_api(_id=_id, user=self.current_user, test=False)
            except (SlugRegistrationError, APIRequestError) as err:
                raise BadRequest(details=str(err))
            except Exception as err:
                raise HTTPError(500, response=str(err))

        self.finish({'success': True, 'details': res})

    def delete(self, _id):
        """
        Delete API

        Args:
            _id: API id to be deleted permanently
        """
        user = self.current_user
        if not user:
            raise HTTPError(401, response='Login required')

        doc = APIDocController(_id=_id)
        try:
            res = doc.delete(_id=_id, user=user)
        except APIRequestError as err:
            raise BadRequest(details=str(err))

        self.finish({'success': True, 'details': res})


class ValueSuggestionHandler(BaseHandler):

    kwargs = {
        'GET': {
            'field': {'type': str, 'default': None},
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
        if not self.args.field:
            raise HTTPError(code=400, response='Request is missing a required parameter: field')

        res = APIDocController.get_tags(self.args.field, self.args.size)
        self.finish(res)


class GitWebhookHandler(BaseHandler):

    data_handler = SmartAPIData()

    def post(self):
        # do message authentication
        digest_obj = hmac.new(key=self.web_settings.API_KEY.encode(
        ), msg=self.request.body, digestmod=hashlib.sha1)
        if not hmac.compare_digest('sha1=' + digest_obj.hexdigest(), self.request.headers.get('X-Hub-Signature', '')):
            self.set_status(405)
            self.finish({'success': False, 'error': 'Invalid authentication'})
            return
        data = tornado.escape.json_decode(self.request.body)
        # get repository owner name
        repo_owner = data.get('repository', {}).get(
            'owner', {}).get('name', None)
        if not repo_owner:
            self.set_status(405)
            self.finish({'success': False, 'error': 'Cannot get repository owner'})
            return
        # get repo name
        repo_name = data.get('repository', {}).get('name', None)
        if not repo_name:
            self.set_status(405)
            self.finish({'success': False, 'error': 'Cannot get repository name'})
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
        ids_refresh = [x['_id'] for x in self.data_handler.fetch_all(query=_query)]
        # if there are any ids to refresh, do it
        if ids_refresh:
            self.data_handler.refresh_all(id_list=ids_refresh, dryrun=False)

