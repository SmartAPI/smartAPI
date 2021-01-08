''' Tornado Web Server Starting Script - Application Entry Point '''

from biothings.web.index_base import main
from tornado.ioloop import IOLoop

from handlers.frontend import APP_LIST
from utils.indices import setup_data


if __name__ == '__main__':
    IOLoop.current().add_callback(setup_data)
    main(APP_LIST, {}, use_curl=True)
