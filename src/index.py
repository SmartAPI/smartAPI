"""
    SmartAPI Web Server Entry Point

        > python index.py

"""

import os.path

from tornado.ioloop import IOLoop, PeriodicCallback
from utils.api_monitor import update_uptime_status
from utils.versioning import backup_and_refresh

import config
from biothings.web.index_base import main
from biothings.web.settings import BiothingESWebSettings

WEB_SETTINGS = BiothingESWebSettings(config=config)

if __name__ == '__main__':
    (SRC_PATH, _) = os.path.split(os.path.abspath(__file__))
    STATIC_PATH = os.path.join(SRC_PATH, 'static')
    IOLoop.current().add_callback(update_uptime_status)
    PeriodicCallback(backup_and_refresh, 24*60*60*1000).start()
    PeriodicCallback(update_uptime_status, 24*60*60*1000, 0.1).start()
    main(WEB_SETTINGS.generate_app_list(),
         app_settings={"cookie_secret": config.COOKIE_SECRET},
         debug_settings={"static_path": STATIC_PATH},
         use_curl=True)
