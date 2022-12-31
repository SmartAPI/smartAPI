from .all_specs_sync_loader import AllSpecsSyncLoader


class SingleSpecSyncLoader(AllSpecsSyncLoader):
    _smartAPIID = ''

    def __init__(self, smartAPIID, path):
        super().__init__(path)
        self._smartAPIID = smartAPIID

    def parse(self, _input):
        return [item for item in _input['hits'] if item['_id'] == self._smartAPIID]
