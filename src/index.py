''' Tornado Web Server Starting Script - Application Entry Point '''


from biothings.web.index_base import main
from tornado.ioloop import IOLoop

from web.handlers import APP_LIST
from web.api.controllers.indices import setup_data

if __name__ == '__main__':
    IOLoop.current().add_callback(setup_data)
    main(APP_LIST, {
        'debug': True,
        'autoreload': True
        # "default_handler_class": TemplateHandler,
        # "default_handler_args": {
        #     "filename": "404.html",
        #     "status_code": 404
        # }
    }, use_curl=True)