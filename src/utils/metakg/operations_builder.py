from .loader import AllSpecsLoader
from .parser.index import API


class OperationsBuilder:
    def build(self):
        specs = self.load()
        return self.load_ops_from_specs(specs)

    def load(self):
        loader = AllSpecsLoader()
        specs = loader.load()
        return specs

    def load_ops_from_specs(self, specs):
        all_ops = []
        for spec in specs:
            parser = API(spec)
            ops = parser.metadata['operations']
            all_ops.extend(ops)
        return all_ops
