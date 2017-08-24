import sys
import os
import tornado.httpserver
import tornado.httpclient
import tornado.ioloop
import tornado.web
import tornado.gen

from jinja2 import Environment, FileSystemLoader

import logging

from tornado.httputil import url_concat
#from tornado.concurrent import return_future

import torngithub
from torngithub import json_encode, json_decode

import config

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


class MainHandler(BaseHandler, torngithub.GithubMixin, tornado.web.RequestHandler):
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
            _next = self.get_argument("next", "/")
            if _next != "/":
                path += "?next={}".format(_next)
            self.redirect(path)
            #
            # xsrf = self.xsrf_token
            # login_file = "login.html"
            # login_template = templateEnv.get_template(login_file)
            # login_output = login_template.render(path=config.GITHUB_CALLBACK_PATH, xsrf=xsrf)
            # self.write(login_output)

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


# Registration Form
REG_FILE = "reg_form.html"
reg_template = templateEnv.get_template(REG_FILE)
reg_output = reg_template.render()


class RegistrationHandler(tornado.web.RequestHandler):
    """
    API Metadata URL registration form.
    """
    def get(self):
        self.write(reg_output)

# class RegistrationHandler(tornado.web.RequestHandler):
#     def get(self):
#         self.write(index_output)


#Login
# LOGIN_FILE = "login.html"
# login_template = templateEnv.get_template(LOGIN_FILE)
# login_output = login_template.render()

# class LoginHandler(tornado.web.RequestHandler):
#     def get(self):
#         self.write(login_output)


# https://stackoverflow.com/questions/12031007/disable-static-file-caching-in-tornado
# class MyStaticFileHandler(tornado.web.StaticFileHandler):
#     def set_extra_headers(self, path):
#         # Disable cache
#         self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')


APP_LIST = [
    (r"/", MainHandler),
    (r"/registration", RegistrationHandler),
    (r"/login", LoginHandler),
    (config.GITHUB_CALLBACK_PATH, GithubLoginHandler),
    (r"/logout", LogoutHandler)
]

'''
settings = {
    "static_path": STATIC_PATH,
    "template_path": TEMPLATE_PATH,
    "compiled_template_cache": False,
    "cookie_secret": "asdf",
    "login_url": options.github_callback_path,
    "xsrf_cookies": True,
    "github_client_id": options.github_client_id,
    "github_client_secret": options.github_client_secret,
    "github_callback_path": options.github_callback_path,
    "github_scope": options.github_scope,
    "autoescape": None
}


def main():
    tornado.httpclient.AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")

    application = tornado.web.Application(APP_LIST, **settings)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port, address=options.address)
    loop = tornado.ioloop.IOLoop.instance()
    if options.debug:
        tornado.autoreload.start(loop)
        logging.info('Server is running on "%s:%s"...' % (options.address, options.port))
    loop.start()


if __name__ == "__main__":
    main()
'''
