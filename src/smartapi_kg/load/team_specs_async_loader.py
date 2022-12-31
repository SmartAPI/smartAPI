from .base_async_loader import BaseAsyncLoader
from ..config import TEAM_SMARTAPI_QUERY_TEMPLATE


class TeamSpecsAsyncLoader(BaseAsyncLoader):
    def __init__(self, team_name):
        super().__init__(TEAM_SMARTAPI_QUERY_TEMPLATE.replace("{team_name}", team_name))

    def fetch(self):
        return super().fetch()

    def parse(self, _input):
        return _input['hits']
