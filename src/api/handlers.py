import json
import datetime

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.escape

from .es import ESQuery
from .transform import get_api_metadata_by_url, APIMetadata


class BaseHandler(tornado.web.RequestHandler):
    def return_json(self, data):
        _json_data = json.dumps(data, indent=2)
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.support_cors()
        self.write(_json_data)

    def support_cors(self, *args, **kwargs):
        '''Provide server side support for CORS request.'''
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.set_header("Access-Control-Allow-Headers", "Content-Type, Depth, User-Agent, X-File-Size, X-Requested-With, If-Modified-Since, X-File-Name, Cache-Control")
        self.set_header("Access-Control-Allow-Credentials", "false")
        self.set_header("Access-Control-Max-Age", "60")

    def options(self, *args, **kwargs):
        self.support_cors()

    def get_current_user(self):
        user_json = self.get_secure_cookie("user").decode('utf-8')
        if not user_json:
            return None
        return json.loads(user_json)


class QueryHanlder(BaseHandler):
    def get(self):
        q = self.get_argument('q', None)
        if not q:
            self.return_json({'success': False, 'error': 'missing required parameter.'})

        fields = self.get_argument('fields', None)
        return_raw = self.get_argument('raw', '').lower() in ['1', 'true']

        esq = ESQuery()
        res = esq.query_api(q=q, fields=fields, return_raw=return_raw)
        self.return_json(res)


class ValidateHanlder(BaseHandler):
    def get(self):
        url = self.get_argument('url', None)
        if url:
            data = get_api_metadata_by_url(url)
            if data and isinstance(data, dict):
                metadata = APIMetadata(data)
                valid = metadata.validate()
                return self.return_json(valid)
            else:
                return self.return_json({"valid": False, "error": "The input url does not contain valid API metadata."})
        else:
            return self.return_json({"valid": False, "error": "Need to provide an input url first."})


class APIHandler(BaseHandler):
    def post(self):
        # check if a logged in user
        user = self.get_current_user()
        if not user:
            res = {'success': False, 'error': 'Authenicate first with your github account.'}
            self.set_status(401)
            self.return_json(res)
        else:
            # save an API metadata
            # api_key = self.get_argument('api_key', None)
            overwrite = self.get_argument('overwrite', '').lower()
            overwrite = overwrite in ['1', 'true']
            dryrun = self.get_argument('dryrun', '').lower()
            dryrun = dryrun in ['on', '1', 'true']
            # if api_key != config.API_KEY:
            #     self.set_status(405)
            #     res = {'success': False, 'error': 'Invalid API key.'}
            #     self.return_json(res)
            # else:
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
                        esq = ESQuery()
                        res = esq.save_api(data, overwrite=overwrite, dryrun=dryrun)
                        self.return_json(res)
                else:
                    self.return_json({'success': False, 'error': 'Invalid input data.'})

            else:
                self.return_json({'success': False, 'error': 'missing required parameter.'})


class APIMetaDataHandler(BaseHandler):
    esq = ESQuery()

    def get(self, api_name):
        '''return API metadata for a matched api_name,
           if api_name is "all", return a list of all APIs
        '''
        fields = self.get_argument('fields', None)
        return_raw = self.get_argument('raw', False)
        with_meta = self.get_argument('meta', False)
        size = self.get_argument('size', None)
        from_ = self.get_argument('from', 0)
        try:
            size = int(size)   # size capped to 100 for now by get_api method below.
        except (TypeError, ValueError):
            size = None
        try:
            from_ = int(from_)
        except (TypeError, ValueError):
            from_ = 0
        if fields:
            fields = fields.split(',')
        res = self.esq.get_api(api_name, fields=fields, with_meta=with_meta, return_raw=return_raw, size=size, from_=from_)
        self.return_json(res)


class ValueSuggestionHandler(BaseHandler):
    esq = ESQuery()

    def get(self):
        field = self.get_argument('field', None)
        try:
            size = int(self.get_argument('size', 100))
        except:
            size = 100
        if field:
            res = self.esq.value_suggestion(field, size=size)
        else:
            res = {'error': 'missing required "field" parameter'}
        self.return_json(res)


APP_LIST = [
    (r'/?', APIHandler),
    (r'/query/?', QueryHanlder),
    (r'/validate/?', ValidateHanlder),
    (r'/metadata/(.+)/?', APIMetaDataHandler),
    (r'/suggestion/?', ValueSuggestionHandler),
]
