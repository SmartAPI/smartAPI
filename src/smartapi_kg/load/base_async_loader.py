import requests
import json
from .base_loader import BaseLoader
from ..exceptions.fail_to_load_spec import FailToLoadSpecError


class BaseAsyncLoader(BaseLoader):
    _url = ''

    def __init__(self, url):
        super().__init__()
        self._url = url

    def fetch(self):
        try:
            response = requests.get(self._url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError:
            raise FailToLoadSpecError(f"Query to ${self._url} failed with status code ${response.status_code}")
        except Exception as e:
            raise Exception(f"Query to ${self._url} failed with error ${str(e)}")

    def parse(self, _input):
        return []

    def load(self):
        specs = self.fetch()
        return self.parse(specs)
