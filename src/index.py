""" SmartAPI Entry Point """

from threading import Thread

from aiocron import crontab
from biothings.web.index_base import main
from tornado.ioloop import IOLoop

from admin import routine
from handlers.frontend import APP_LIST
from utils.indices import setup


def run_routine():
    thread = Thread(target=routine, daemon=True)
    thread.start()


if __name__ == '__main__':

    crontab('0 0 * * *', func=run_routine, start=True)
    IOLoop.current().add_callback(setup)
    main(APP_LIST, use_curl=True)
