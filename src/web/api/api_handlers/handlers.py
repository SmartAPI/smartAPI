
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
from tornado.httpclient import HTTPError, HTTPResponse
# from biothings.web.handlers.exceptions import BadRequest

# from .es import ESQuery
from web.api.transform import APIMetadata, get_api_metadata_by_url

from utils.slack_notification import send_slack_msg

from web.api.controllers.controller import APIDocController
from web.api.controllers.controller import RegistrationError


class BaseHandler(BaseESRequestHandler):

    def get_current_user(self):
        user_json = self.get_secure_cookie("user")
        if not user_json:
            return None
        return json.loads(user_json.decode('utf-8'))


class APIHandler(BaseHandler):
    def post(self):
        """
        Add an API doc /api

        Raises:
            HTTPError: url not working
            BadRequest: failed validation
            HTTPError: server error

        Returns:
            Success: Bool
        """
        # check if a logged in user
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
                        except RegistrationError as err:
                            raise RegistrationError(**err.to_dict())
                        except Exception as err:  # unexpected
                            raise HTTPError(500, response=str(err))

                        if(res and not dryrun):
                            # might need to move to controller
                            self.return_json({'success': True, 'dryrun': False})
                            send_slack_msg(data, res, user['login'])
                        else:
                            # Dryrun
                            self.return_json(res)
                else:
                    raise HTTPError(code=400, 
                                response={'success': False,
                                          'error': 'API metadata is not in a valid format'})

            else:
                raise HTTPError(code=400, 
                                response={'success': False,
                                          'error': 'Request is missing a required parameter: url'})
                


APP_LIST = [
    (r'/?', APIHandler),
#     (r'/query/?', BioThingsESQueryHandler),
#     (r'/validate/?', ValidateHandler),
#     (r'/metadata/(.+)/?', APIMetaDataHandler),
#     (r'/suggestion/?', ValueSuggestionHandler),
#     (r'/webhook_payload/?', GitWebhookHandler),
]
