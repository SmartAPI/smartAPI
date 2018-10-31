import sys
import os.path
import json

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.escape
from tornado.options import define, options

from api.handlers import APP_LIST as api_app_list
from web.handlers import APP_LIST as web_app_list
import config

src_path = os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]
if src_path not in sys.path:
    sys.path.append(src_path)
print(src_path)

STATIC_PATH = os.path.join(src_path, 'src/static')

define("port", default=8000, help="run on the given port", type=int)
define("address", default="127.0.0.1", help="run on localhost")
define("debug", default=False, type=bool, help="run in debug mode")
tornado.options.parse_command_line()
if options.debug:
    import tornado.autoreload
    import logging
    logging.getLogger().setLevel(logging.DEBUG)
    options.address = '0.0.0.0'


def get_json(filename):
    with open(filename) as f:
        return json.load(f)


def add_apps(prefix='', app_list=[]):
    '''
    Add prefix to each url handler specified in app_list.
    add_apps('test', [('/', testhandler,
                      ('/test2', test2handler)])
    will return:
                     [('/test/', testhandler,
                      ('/test/test2', test2handler)])
    '''
    if prefix:
        return [('/'+prefix+url, handler) for url, handler in app_list]
    else:
        return app_list


APP_LIST = [
    # (r"/", MainHandler),
]

APP_LIST += add_apps('', web_app_list)
APP_LIST += add_apps('api', api_app_list)


settings = {
    "cookie_secret": config.COOKIE_SECRET
}
if options.debug:
    settings.update({
        "static_path": STATIC_PATH,
        "debug": True
    })


def main():
    # required for proper github oauth authentication
    # ref: https://github.com/jkeylu/torngithub
    tornado.httpclient.AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")

    application = tornado.web.Application(APP_LIST, **settings)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port, address=options.address)
    loop = tornado.ioloop.IOLoop.instance()
    if options.debug:
        # tornado.autoreload.start(loop)
        logging.info('Server is running on "%s:%s"...' % (options.address, options.port))
    loop.start()


if __name__ == "__main__":
    main()
