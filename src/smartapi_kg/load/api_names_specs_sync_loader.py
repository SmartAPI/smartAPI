from .all_specs_sync_loader import AllSpecsSyncLoader


class APINamesSpecsSyncLoader(AllSpecsSyncLoader):
    _api_names = []

    def __init__(self, api_names, path):
        super().__init__(path)
        self._api_names = api_names

    def parse(self, _input):
        return [item for item in _input['hits'] if item['info']['title'] in self._api_names]
