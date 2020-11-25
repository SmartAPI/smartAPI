''' Tornado Web Server Starting Script - Application Entry Point '''


from biothings.web.index_base import main
from tornado.ioloop import IOLoop

from web.handlers import APP_LIST


if __name__ == '__main__':

    main(APP_LIST, {
        # "default_handler_class": TemplateHandler,
        # "default_handler_args": {
        #     "filename": "404.html",
        #     "status_code": 404
        # }
    }, use_curl=True)