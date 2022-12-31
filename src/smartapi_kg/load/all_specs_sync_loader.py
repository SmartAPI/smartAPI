import json
from .base_loader import BaseLoader


class AllSpecsSyncLoader(BaseLoader):
    _file_path = ''

    def __init__(self, path):
        super().__init__()
        self._file_path = path

    def fetch(self):
        with open(self._file_path, encoding='utf-8') as file:
            data = json.load(file)
            if 'hits' not in data:
                result = {
                    'hits': [data],
                }
            else:
                result = data
            return result

    def parse(self, _input):
        return _input['hits']

    def load(self):
        specs = self.fetch()
        return self.parse(specs)
