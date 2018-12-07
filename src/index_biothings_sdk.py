from biothings.web.index_base import main, options
# from web.settings import MyPharmgkb_GeneWebSettings

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
# Instantiate settings class to configure biothings web
# web_settings = MyPharmgkb_GeneWebSettings(config='config')

if __name__ == '__main__':
    # set debug level on app settings
    # web_settings.set_debug_level(options.debug)
    # main(web_settings.generate_app_list(), debug_settings={"STATI_PACTH": web_settings.STATIC_PATH, "debug": True},
    #      sentry_client_key=web_settings.SENTRY_CLIENT_KEY)
    src_path = os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]
    static_path = os.path.join(src_path, 'src', 'static')
    print(static_path)
    main(APP_LIST, 
        app_settings={"cookie_secret": config.COOKIE_SECRET}, 
        debug_settings={"static_path":static_path,"debug": True},
        http_client='curl')