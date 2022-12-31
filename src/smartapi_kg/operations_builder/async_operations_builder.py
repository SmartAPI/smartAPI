from .base_operations_builder import BaseOperationsBuilder
from ..load.async_loader_factory import async_loader_factory


class AsyncOperationsBuilder(BaseOperationsBuilder):
    def __init__(self, options):
        super().__init__(options)

    def load(self):
        specs = async_loader_factory(
            self._options.get('smart_API_id'),
            self._options.get('team_name'),
            self._options.get('tag'),
            self._options.get('component'),
        )

        return specs

    def build(self):
        specs = self.load()
        return self.load_ops_from_specs(specs)
