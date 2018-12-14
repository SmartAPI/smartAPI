from biothings.web.index_base import main, options
from biothings.web.settings import BiothingESWebSettings
import os.path
import config

web_settings = BiothingESWebSettings(config=config)

if __name__ == '__main__':
    (src_path, _) = os.path.split(os.path.abspath(__file__))
    static_path = os.path.join(src_path, 'static')
    main(web_settings.generate_app_list(),
         app_settings={"cookie_secret": config.COOKIE_SECRET},
         debug_settings={"static_path": static_path},
         use_curl=True)

