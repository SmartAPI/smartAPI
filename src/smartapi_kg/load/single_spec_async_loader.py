from .base_async_loader import BaseAsyncLoader
from ..config import SINGLE_API_SMARTAPI_QUERY_TEMPLATE


class SingleSpecAsyncLoader(BaseAsyncLoader):
    _smartapi_id = ''
    
    def __init__(self, smartapi_id):
        super().__init__(SINGLE_API_SMARTAPI_QUERY_TEMPLATE.replace("{smartapi_id}", smartapi_id))
        self._smartapi_id = smartapi_id

    def fetch(self):
        return super().fetch()

    def parse(self, _input):
        _input['_id'] = self._smartapi_id
        return [_input]
