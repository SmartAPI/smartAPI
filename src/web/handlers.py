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
from jinja2 import Environment, FileSystemLoader
from tornado.httputil import url_concat
from torngithub import json_decode, json_encode

from web.api.es import ESQuery
from biothings.web.api.helper import BaseHandler as BioThingsBaseHandler

log = logging.getLogger("smartapi")


src_path = os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]
if src_path not in sys.path:
    sys.path.append(src_path)

TEMPLATE_PATH = os.path.join(src_path, 'templates/')
AVAILABLE_TAGS = ['translator', 'nihdatacommons']

# your Github application Callback
GITHUB_CALLBACK_PATH = "/oauth"
GITHUB_SCOPE = ""

# Docs: http://docs.python-guide.org/en/latest/scenarios/web/
# Load template file templates/site.html
templateLoader = FileSystemLoader(searchpath=TEMPLATE_PATH)
templateEnv = Environment(loader=templateLoader, cache_size=0)


class BaseHandler(BioThingsBaseHandler):
    def get_current_user(self):
        user_json = self.get_secure_cookie("user")
        if not user_json:
            return None
        return json_decode(user_json)


class MainHandler(BaseHandler):
    def get(self):
        slug = self.request.host.split(".")[0]
        # print("Host: {} - Slug: {}".format(self.request.host, slug))
        if slug.lower() not in ['www', 'dev', 'smart-api']:
            # try to get a registered subdomain/tag
            esq = ESQuery()
            api_id = esq.get_api_id_from_slug(slug)
            if api_id:
                swaggerUI_file = "smartapi-ui.html"
                swagger_template = templateEnv.get_template(swaggerUI_file)
                swagger_output = swagger_template.render(apiID=api_id)
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
        path = GITHUB_CALLBACK_PATH
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


class RegistryHandler(BaseHandler):
    def get(self, tag=None):
        template_file = "smart-registry.html"
        # template_file = "/smartapi/dist/index.html"
        reg_template = templateEnv.get_template(template_file)
        # author filter parsing
        if self.get_argument('owners', False):
            owners = [x.strip().lower()
                      for x in self.get_argument('owners').split(',')]
        else:
            owners = []
        # special url tag
        if tag:
            if tag.lower() in AVAILABLE_TAGS:
                # print("tags: {}".format([tag.lower()]))
                reg_output = reg_template.render(Context=json.dumps(
                    {"Tags": [tag.lower()],
                     "Special": True,
                     "Owners": owners}))
            else:
                raise tornado.web.HTTPError(404)
        # typical query filter tags
        elif self.get_argument('tags', False) or \
                self.get_argument('owners', False):
            tags = [x.strip().lower()
                    for x in self.get_argument('tags', "").split(',')]
            # print("tags: {}".format(tags))
            reg_output = reg_template.render(
                Context=json.dumps(
                    {"Tags": tags,
                     "Special": False,
                     "Owners": owners}))
        else:
            reg_output = reg_template.render(Context=json.dumps({}))
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
    def get(self, yourApiID=None):
        if not yourApiID:
            if self.get_argument('url', False):
                api_id = self.get_argument('url').split('/')[-1]
                self.redirect('/ui/{}'.format(api_id), permanent=True)
            else:
                raise tornado.web.HTTPError(404)
            return
        swaggerUI_file = "smartapi-ui.html"
        swagger_template = templateEnv.get_template(swaggerUI_file)
        swagger_output = swagger_template.render(apiID=yourApiID)
        self.write(swagger_output)


class BrandingHandler(BaseHandler):
    def get(self):
        doc_file = "brand.html"
        branding_template = templateEnv.get_template(doc_file)
        branding_output = branding_template.render()
        self.write(branding_output)


class GuideHandler(BaseHandler):
    def get(self):
        doc_file = "guide.html"
        guide_template = templateEnv.get_template(doc_file)
        guide_output = guide_template.render()
        self.write(guide_output)


class APIEditorHandler(BaseHandler):
    def get(self, yourApiID=None):
        if not yourApiID:
            if self.get_argument('url', False):
                api_id = self.get_argument('url').split('/')[-1]
                self.redirect('/editor/{}'.format(api_id), permanent=True)
            else:
                # raise tornado.web.HTTPError(404)
                swaggerEditor_file = "editor.html"
                swagger_template = templateEnv.get_template(swaggerEditor_file)
                swagger_output = swagger_template.render(
                    Context=json.dumps({"Id": '', "Data": False}))
                self.write(swagger_output)
            return
        swaggerEditor_file = "editor.html"
        swagger_template = templateEnv.get_template(swaggerEditor_file)
        swagger_output = swagger_template.render(
            Context=json.dumps({"Id": yourApiID, "Data": True}))
        self.write(swagger_output)


class AboutHandler(BaseHandler):
    def get(self):
        doc_file = "about.html"
        about_template = templateEnv.get_template(doc_file)
        about_output = about_template.render()
        self.write(about_output)

class PrivacyHandler(BaseHandler):
    def get(self):
        doc_file = "privacy.html"
        privacy_template = templateEnv.get_template(doc_file)
        privacy_output = privacy_template.render()
        self.write(privacy_output)

class FAQHandler(BaseHandler):
    def get(self):
        doc_file = "faq.html"
        faq_template = templateEnv.get_template(doc_file)
        faq_output = faq_template.render()
        self.write(faq_output)

class TemplateHandler(BaseHandler):

    def initialize(self, filename, status_code=200, env=None):

        self.filename = filename
        self.status = status_code

    def get(self, **kwargs):

        template = self.env.get_template(self.filename)
        output = template.render(Context=json.dumps(kwargs))

        self.set_status(self.status)
        self.write(output)

class PortalHandler(BaseHandler):

    def get(self, portal=None):
        portals = ['translator']

        template_file = "portal.html"
        reg_template = templateEnv.get_template(template_file)

        if portal in portals:
            reg_output = reg_template.render(Context=json.dumps(
                {"portal": portal}))
        else:
            raise tornado.web.HTTPError(404)
        self.write(reg_output)

APP_LIST = [
    (r"/", MainHandler),
    (r"/user/?", UserInfoHandler),
    (r"/add_api/?", AddAPIHandler),
    (r"/login/?", LoginHandler),
    (GITHUB_CALLBACK_PATH, GithubLoginHandler),
    (r"/logout/?", LogoutHandler),
    (r"/registry/(.+)/?", RegistryHandler),
    (r"/registry/?", RegistryHandler),
    (r"/documentation/?", DocumentationHandler),
    (r"/dashboard/?", DashboardHandler),
    (r"/ui/(.+)/?", SwaggerUIHandler),
    (r"/ui/?", SwaggerUIHandler),
    (r"/branding/?", BrandingHandler),
    (r"/guide/?", GuideHandler),
    (r"/editor/(.+)/?", APIEditorHandler),
    (r"/editor/?", APIEditorHandler),
    (r"/about/?", AboutHandler),
    (r"/faq/?", FAQHandler),
    (r"/privacy/?", PrivacyHandler),
    # (r"/portal/?", TemplateHandler, {"filename": "registry.html"}),
    (r"/portal/(.+)/?", PortalHandler),
]
