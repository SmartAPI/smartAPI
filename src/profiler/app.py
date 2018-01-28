# Import to enable Python2/3 compatible code
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from future.utils import iteritems

import sys, os
from tornado.web import Application, StaticFileHandler
import tornado.httpserver
import tornado.ioloop
from tornado.options import define, options, parse_command_line
import tornado.web
from tornado.escape import json_encode, json_decode

from jinja2 import Environment, FileSystemLoader, TemplateNotFound

import re
import logging

from scripts import profiling, miriam_datatype_identifiers, \
    test_patterns, data_registry_urls


# Define directory paths
src_path = os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]
if src_path not in sys.path:
    sys.path.append(src_path)

actual_path = os.path.dirname(os.path.realpath(__file__))

STATIC_PATH = os.path.join(src_path, 'profiler/static')
TEMPLATE_PATH = os.path.join(src_path, 'profiler/templates')


# Set app configuration
define("port", default=8888, help="run on the given port", type=int)
define("address", default="127.0.0.1", help="run on localhost")
define("debug", default=False, type=bool, help="run in debug mode")


# Handle commandline arguments
tornado.options.parse_command_line()
if options.debug:
    import tornado.autoreload
    import logging
    logging.getLogger().setLevel(logging.DEBUG)
options.address = '0.0.0.0'


class TemplateRendering:
    """
    A simple class to hold methods for rendering templates.
    """
    def render_template(self, template_name, **kwargs):
        template_dirs = []
        if self.settings.get('template_path', ''):
            template_dirs.append(
                self.settings["template_path"]
            )

        env = Environment(loader=FileSystemLoader(template_dirs))

        try:
            template = env.get_template(template_name)
        except TemplateNotFound:
            raise TemplateNotFound(template_name)
        content = template.render(kwargs)
        return content


class BaseHandler(tornado.web.RequestHandler, TemplateRendering):
    """
    RequestHandler already has a `render()` method. I'm writing another
    method `render2()` and keeping the API almost same.
    """
    def render2(self, template_name, **kwargs):
        """
        This is for making some extra context variables available to
        the template
        """
        kwargs.update({
            'settings': self.settings,
            'STATIC_URL': self.settings.get('static_url_prefix', '/static/'),
            'request': self.request,
            'xsrf_token': self.xsrf_token,
            'xsrf_form_html': self.xsrf_form_html,
        })
        content = self.render_template(template_name, **kwargs)
        self.write(content)


class MainHandler(BaseHandler):
    logging.info("** MainHandler called")

    def get(self):
        """ Display form to input web service to annotate. """
        return self.render2('profiler.html')

    def post(self):
        """ Display annotation results. """
        ws_input = self.get_argument('ws_input', '')

        global demo_output
        demo_output = profiling.main(ws_input)

        # Get master_identifier_dictionary for value display in result page
        api_calls = profiling.get_calls_from_form(ws_input)
        master_id_dictionary = profiling.build_api_profile(api_calls)

        # Build dictionary of MIRIAM datatypes
        miriam_datatype_obj = miriam_datatype_identifiers.get_miriam_datatypes()  # noqa
        miriam_name_dict = miriam_datatype_identifiers.build_miriam_name_dictionary(miriam_datatype_obj)  # noqa

        # Get regex pattern data
        all_pattern_data = test_patterns.get_all_pattern_data()
        all_pattern_dict = test_patterns.make_pattern_dictionary(all_pattern_data)  # noqa

        # Get dictionary of MIRIAM Ids and namespace URLs
        data_registry_id_url_dict = data_registry_urls.build_miriam_url_dictionary()  # noqa

        return self.render2(
            'annotation_results.html',
            ws_input=ws_input,
            demo_output=demo_output,
            master_id_dictionary=master_id_dictionary,
            miriam_name_dict=miriam_name_dict,
            all_pattern_dict=all_pattern_dict,
            re=re,
            iteritems=iteritems,
            json_encode=json_encode, json_decode=json_decode,
            data_registry_id_url_dict=data_registry_id_url_dict
        )


class MyStaticFileHandler(tornado.web.StaticFileHandler):
    def set_extra_headers(self, path):
        # Disable cache
        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')


APP_LIST = [
    (r"/", MainHandler)  #change to /profiler when committed to WebsmartAPI, Was r"/"
]

settings = {
    "static_path": STATIC_PATH,
    "template_path": TEMPLATE_PATH
}


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

