from .base_operations_builder import BaseOperationsBuilder
from ..load.sync_loader_factory import sync_loader_factory


class SyncOperationsBuilder(BaseOperationsBuilder):
    _file_path = ''

    def __init__(self, options, path):
        super().__init__(options)
        self._file_path = path

    def build(self):
        specs = sync_loader_factory(
            self._options.get('smart_API_id') or self._options.get('smartAPIID'),
            self._options.get('team_name') or self._options.get('teamName'),
            self._options.get('tag'),
            self._options.get('component'),
            self._options.get('api_names'),
            self._file_path,
        )

        return self.load_ops_from_specs(specs)
