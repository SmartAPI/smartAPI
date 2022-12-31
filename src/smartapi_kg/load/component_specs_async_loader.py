from .base_async_loader import BaseAsyncLoader
from ..config import COMPONENT_SMARTAPI_QUERY_TEMPLATE


class ComponentSpecsAsyncLoader(BaseAsyncLoader):
    def __init__(self, component):
        super().__init__(COMPONENT_SMARTAPI_QUERY_TEMPLATE.replace("{component_name}", component))

    def fetch(self):
        return super().fetch()

    def parse(self, _input):
        return _input['hits']
