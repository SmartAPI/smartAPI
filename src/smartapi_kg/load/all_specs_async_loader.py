from ..config import SMARTAPI_URL
from .base_async_loader import BaseAsyncLoader


class AllSpecsAsyncLoader(BaseAsyncLoader):
    def __init__(self):
        super().__init__(SMARTAPI_URL)

    def fetch(self):
        return super().fetch()

    def parse(self, _input):
        return _input['hits']

