import json
import logging

from biothings.web.auth.oauth_mixins import GithubOAuth2Mixin
from biothings.web.handlers import BaseAPIHandler
from tornado.httputil import url_concat


class GitHubLoginHandler(BaseAPIHandler, GithubOAuth2Mixin):
    """ "Handler for GitHub oauth login"""

    SCOPES = []
    GITHUB_CALLBACK_PATH = "/oauth"

    async def get(self):
        CLIENT_ID = self.biothings.config.GITHUB_CLIENT_ID
        CLIENT_SECRET = self.biothings.config.GITHUB_CLIENT_SECRET
        code = self.get_argument("code", None)
        redirect_uri = url_concat(
            self.request.protocol + "://" + self.request.host + self.GITHUB_CALLBACK_PATH,
            {"next": self.get_argument("next", "/")},
        )
        if code is None:
            logging.info("Redirecting to login...")
            self.authorize_redirect(
                redirect_uri=redirect_uri,
                client_id=CLIENT_ID,
                scope=self.SCOPES,
            )
        else:
            logging.info("got code, try to get token")
            token = await self.github_get_oauth2_token(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, code=code)
            user = await self.github_get_authenticated_user(token["access_token"])
            user = self._format_user_record(user)
            logging.info("Got user info: {}".format(user))
            if user:
                logging.info("Setting user cookie.")
                self.set_secure_cookie("user", user)
            else:
                logging.info("Failed to get user info.")
                self.clear_cookie("user")
            self.redirect(self.get_argument("next", "/"))

    def _format_user_record(self, user):
        user_data = {}
        user_data["login"] = user.get("login")
        if not user_data["login"]:
            return
        if user.get("name"):
            user_data["name"] = user["name"]
        if user.get("email"):
            user_data["email"] = user["email"]
        if user.get("avatar_url"):
            user_data["avatar_url"] = user["avatar_url"]
        if user.get("company"):
            user_data["organization"] = user["company"]
        return json.dumps(user_data)
