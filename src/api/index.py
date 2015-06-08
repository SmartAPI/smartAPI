import sys
import os.path
import subprocess
import json

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.escape
from tornado.options import define, options
from pyld import jsonld

from es import ESQuery

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


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        #self.write('hello world!')
        #self.render(os.path.join(src_path, '../alpaca.htm'))
        self.redirect('/website/')


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


class JsonHandler(BaseHandler):
    def get(self, ctx_name):
        if ctx_name == 'mygene':
            obj = get_json(os.path.join(src_path, '../data/mygene.info.smartAPI.json'))
            #del obj['services'][0]['@context']
            obj = jsonld.expand(obj)[0]
            self.return_json(obj)
        elif ctx_name == '2':
            obj = get_json(os.path.join(src_path, '../data/mygene.info.smartAPI.json'))
            obj = jsonld.expand(obj['services'][0])
            self.return_json(obj)
        elif ctx_name == '3':
            obj = get_json(os.path.join(src_path, '../data/mygene.info.smartAPI.json'))
            obj = jsonld.expand(obj['services'][0])
            self.return_json(obj)
        if ctx_name == 'myvariant':
            obj = get_json(os.path.join(src_path, '../data/myvariant.info.smartAPI.json'))
            #del obj['services'][0]['@context']
            obj = jsonld.expand(obj)[0]
            self.return_json(obj)


class QueryHanlder(BaseHandler):
    def get(self):
        q = self.get_argument('q', None)
        fields = self.get_argument('fields', None)
        input = self.get_argument('input', '1').lower() in ['1', 'true']

        esq = ESQuery(es_host='su07:9200')
        res = esq.query_api(q=q, fields=fields, input=input)
        self.return_json(res)


class APIHandler(BaseHandler):
    def post(self):
        #data = self.request.arguments
        data = tornado.escape.json_decode(self.request.body)
        print(json.dumps(data, indent=2))
        self.return_json({'success': True})

class PathHanlder(BaseHandler):
    def get(self):
        _from = self.get_argument('from', None)
        _to = self.get_argument('to', None)
        if _from and _to:
            #self.write("<b>{}</b>&#x2192;<b>MyVariant.info</b>&#x2192;<b>hgnc.symbol</b>&#x2192;<b>MyGene.info</b>&#x2192;<b>{}</b>".format(_from, _to))
            if _from == 'variant_id' and _to == 'pfam':
                self.render(os.path.join(src_path, '../graph.htm'))
            else:
                self.write('No proper API path found!')
        else:
            self.write("Missing parameters!")



APP_LIST = [
    (r"/", MainHandler),
    (r'/json/(.+)/?', JsonHandler),
    (r'/query/?', QueryHanlder),
    (r'/api/?', APIHandler),
    (r'/path/?', PathHanlder),
]

settings = {}
if options.debug:
    settings.update({
        "static_path": STATIC_PATH,
    })


def main():
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
