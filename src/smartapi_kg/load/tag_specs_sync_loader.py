from .all_specs_sync_loader import AllSpecsSyncLoader


class TagSpecsSyncLoader(AllSpecsSyncLoader):
    _tag = ''

    def __init__(self, tag, path):
        super().__init__(path)
        self._tag = tag

    def parse(self, _input):
        return [item for item in _input['hits'] for tag in item['tags'] if self._tag == tag['name']]
