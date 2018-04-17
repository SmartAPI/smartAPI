import sys
import os

import tornado.httpserver
import tornado.httpclient
import tornado.ioloop
import tornado.web
import tornado.gen
from tornado.httputil import url_concat
from jinja2 import Environment, FileSystemLoader
import torngithub
from torngithub import json_encode, json_decode

import config

import logging
log = logging.getLogger("smartapi")


src_path = os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]
if src_path not in sys.path:
    sys.path.append(src_path)

TEMPLATE_PATH = os.path.join(src_path, 'templates/')


# Docs: http://docs.python-guide.org/en/latest/scenarios/web/
# Load template file templates/site.html
templateLoader = FileSystemLoader(searchpath=TEMPLATE_PATH)
templateEnv = Environment(loader=templateLoader, cache_size=0)


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        user_json = self.get_secure_cookie("user")
        if not user_json:
            return None
        return json_decode(user_json)

    def return_json(self, data):
        _json_data = json_encode(data)
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.write(_json_data)


class MainHandler(BaseHandler):
    def get(self):
        subdomain = self.request.host.split(".")[0]
        if subdomain not in ['www', 'dev', 'smart-api']:
            # try to get a registered subdomains
            if subdomain.lower() in config.REGISTERED_SUBDOMAINS:
                swaggerUI_file = "smartapi-ui.html"
                swagger_template = templateEnv.get_template(swaggerUI_file)
                swagger_output = swagger_template.render(apiID = config.REGISTERED_SUBDOMAINS[subdomain.lower()])
                self.write(swagger_output)
                return
        index_file = "index.html"
        index_template = templateEnv.get_template(index_file)
        index_output = index_template.render()
        self.write(index_output)


class UserInfoHandler(BaseHandler):
    def get(self):
        current_user = self.get_current_user() or {}
        for key in ['access_token', 'id']:
            if key in current_user:
                del current_user[key]
        self.return_json(current_user)


class LoginHandler(BaseHandler):
    def get(self):
        xsrf = self.xsrf_token
        login_file = "login.html"
        login_template = templateEnv.get_template(login_file)
        path = config.GITHUB_CALLBACK_PATH
        _next = self.get_argument("next", "/")
        if _next != "/":
            path += "?next={}".format(_next)
        login_output = login_template.render(path=path, xsrf=xsrf)
        self.write(login_output)


class AddAPIHandler(BaseHandler, torngithub.GithubMixin):
    # def get(self):
        # self.write("Hello, world")
        # self.write(html_output)
        # template.render(list=movie_list,
        #                 title="Here is my favorite movie list")
    def get(self):
        if self.current_user:
            # self.write('Login User: ' +  self.current_user["name"]
            #            + '<br> Email: ' + self.current_user["email"]
            #            + ' <a href="/logout">Logout</a>')
            template_file = "reg_form.html"
            reg_template = templateEnv.get_template(template_file)
            reg_output = reg_template.render()
            self.write(reg_output)
        else:
            path = '/login'
            _next = self.get_argument("next", self.request.path)
            if _next != "/":
                path += "?next={}".format(_next)
            self.redirect(path)


class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("user")
        self.redirect(self.get_argument("next", "/"))


class GithubLoginHandler(tornado.web.RequestHandler, torngithub.GithubMixin):
    @tornado.gen.coroutine
    def get(self):
        # we can append next to the redirect uri, so the user gets the
        # correct URL on login
        redirect_uri = url_concat(self.request.protocol +
                                  "://" + self.request.host +
                                  config.GITHUB_CALLBACK_PATH,
                                  {"next": self.get_argument('next', '/')})

        # if we have a code, we have been authorized so we can log in
        if self.get_argument("code", False):
            user = yield self.get_authenticated_user(
                redirect_uri=redirect_uri,
                client_id=config.GITHUB_CLIENT_ID,
                client_secret=config.GITHUB_CLIENT_SECRET,
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
            client_id=config.GITHUB_CLIENT_ID,
            extra_params={"scope": config.GITHUB_SCOPE, "foo": 1}
        )


class RegistryHandler(BaseHandler):
    def get(self):
        template_file = "registry.html"
        reg_template = templateEnv.get_template(template_file)
        reg_output = reg_template.render()
        self.write(reg_output)

class DocumentationHandler(BaseHandler):
    def get(self):
        doc_file = "documentation.html"
        documentation_template = templateEnv.get_template(doc_file)
        documentation_output = documentation_template.render()
        self.write(documentation_output)

class DashboardHandler(BaseHandler):
    def get(self):
        doc_file = "dashboard.html"
        dashboard_template = templateEnv.get_template(doc_file)
        dashboard_output = dashboard_template.render()
        self.write(dashboard_output)

class SwaggerUIHandler(BaseHandler):
    def get(self, yourApiID):
        swaggerUI_file = "smartapi-ui.html"
        swagger_template = templateEnv.get_template(swaggerUI_file)
        swagger_output = swagger_template.render(apiID = yourApiID )
        self.write(swagger_output)

APP_LIST = [
    (r"/", MainHandler),
    (r"/user/?", UserInfoHandler),
    (r"/add_api/?", AddAPIHandler),
    (r"/login/?", LoginHandler),
    (config.GITHUB_CALLBACK_PATH, GithubLoginHandler),
    (r"/logout/?", LogoutHandler),
    (r"/registry/?", RegistryHandler),
    (r"/documentation/?", DocumentationHandler),
    (r"/dashboard/?", DashboardHandler),
    (r"/api-ui/(.+)/?", SwaggerUIHandler),
    (r"/ui/(.+)/?", SwaggerUIHandler)
]
