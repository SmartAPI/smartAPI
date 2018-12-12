from biothings.web.index_base import main, options

from api.handlers import APP_LIST as api_app_list
from web.handlers import APP_LIST as web_app_list

import os.path
import config


def add_apps(prefix='', app_list=None):
    '''
    Add prefix to each url handler specified in app_list.
    add_apps('test', [('/', testhandler,
                      ('/test2', test2handler)])
    will return:
                     [('/test/', testhandler,
                      ('/test/test2', test2handler)])
    '''
    if not app_list:
        app_list = []
    if prefix:
        return [('/'+prefix+url, handler) for url, handler in app_list]
    else:
        return app_list


APP_LIST = [
    # (r"/", MainHandler),
]

APP_LIST += add_apps('', web_app_list)
APP_LIST += add_apps('api', api_app_list)

if __name__ == '__main__':
    (src_path, _) = os.path.split(os.path.abspath(__file__))
    static_path = os.path.join(src_path, 'static')
    main(APP_LIST,
         app_settings={"cookie_secret": config.COOKIE_SECRET},
         debug_settings={"static_path": static_path},
         select_curl=True)
