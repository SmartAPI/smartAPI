import json
import logging
import os
import sys

import tornado.gen
import tornado.httpclient
import tornado.httpserver
import tornado.ioloop
import tornado.web
import torngithub
from biothings.web.handlers import BaseHandler as BioThingsBaseHandler
from tornado.httputil import url_concat
from torngithub import json_decode, json_encode

from controller import SmartAPI

log = logging.getLogger("smartapi")

src_path = os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]
if src_path not in sys.path:
    sys.path.append(src_path)

STATICPATH = os.path.join(src_path, './web-app/dist')

# your Github application Callback
GITHUB_CALLBACK_PATH = "/oauth"
GITHUB_SCOPE = ""



class BaseHandler(BioThingsBaseHandler):
    def get_current_user(self):
        user_json = self.get_secure_cookie("user")
        if not user_json:
            return None
        return json_decode(user_json)

class MainHandler(BaseHandler):
    def get(self, page=None):
        self.render(STATICPATH + '/index.html')

class Filehandler(tornado.web.StaticFileHandler):
    def initialize(self, path):
        self.dirname, self.filename = os.path.split(path)
        super(Filehandler, self).initialize(self.dirname)

    def get(self, path=None, include_body=True):
        # Ignore 'path'.
        super(Filehandler, self).get(self.filename, include_body)

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


class GithubLoginHandler(BaseHandler, torngithub.GithubMixin):

    @tornado.gen.coroutine
    def get(self):
        # we can append next to the redirect uri, so the user gets the
        # correct URL on login
        redirect_uri = url_concat(self.request.protocol +
                                  "://" + self.request.host +
                                  GITHUB_CALLBACK_PATH,
                                  {"next": self.get_argument('next', '/')})

        # if we have a code, we have been authorized so we can log in
        if self.get_argument("code", False):
            user = yield self.get_authenticated_user(
                redirect_uri=redirect_uri,
                client_id=self.web_settings.GITHUB_CLIENT_ID,
                client_secret=self.web_settings.GITHUB_CLIENT_SECRET,
                code=self.get_argument("code")
            )
            if user:
                log.info('logged in user from github: ' + str(user))
                self.set_secure_cookie("user", json_encode(user))
            else:
                self.clear_cookie("user")
            self.redirect(self.get_argument("next", "/"))
            return

        # otherwise we need to request an authorization code
        yield self.authorize_redirect(
            redirect_uri=redirect_uri,
            client_id=self.web_settings.GITHUB_CLIENT_ID,
            extra_params={"scope": GITHUB_SCOPE, "foo": 1}
        )




APP_LIST = [
    (r"/", MainHandler),
    (r"/user/?", UserInfoHandler),
    (r"/login/?", LoginHandler),
    (GITHUB_CALLBACK_PATH, GithubLoginHandler),
    (r"/logout/?", LogoutHandler),
    (r"/css/(.*)", tornado.web.StaticFileHandler, {"path": STATICPATH + '/css'}),
    (r"/js/(.*)", tornado.web.StaticFileHandler, {"path": STATICPATH + '/js'}),
    (r"/img/(.*)", tornado.web.StaticFileHandler, {"path": STATICPATH + '/img'}),
    (r"/fonts/(.*)", tornado.web.StaticFileHandler, {"path": STATICPATH + '/fonts'}),
    (r'/favicon\.ico', Filehandler, {'path': STATICPATH + '/img/icons' }),
    # in case of reload SPA can handle proper routing
    (r"/(.+)?", MainHandler),
]
