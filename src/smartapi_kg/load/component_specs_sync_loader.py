from .all_specs_sync_loader import AllSpecsSyncLoader


class ComponentSpecsSyncLoader(AllSpecsSyncLoader):
    _component = ''

    def __init__(self, component, path):
        super().__init__(path)
        self._component = component

    def parse(self, _input):
        return [item for item in _input['hits'] if "x-translator" in item['info'] and
                item['info']["x-translator"]['component'] == self._component]
