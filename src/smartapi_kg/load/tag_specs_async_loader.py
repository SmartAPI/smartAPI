from .base_async_loader import BaseAsyncLoader
from ..config import TAG_SMARTAPI_QUERY_TEMPLATE


class TagSpecsAsyncLoader(BaseAsyncLoader):
    def __init__(self, tag):
        super().__init__(TAG_SMARTAPI_QUERY_TEMPLATE.replace("{tag_name}", tag))

    def fetch(self):
        return super().fetch()

    def parse(self, _input):
        return _input['hits']
