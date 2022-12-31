from abc import ABC, abstractmethod

from ..parser.index import API


class BaseOperationsBuilder(ABC):
    _options = {}

    def __init__(self, options):
        self._options = options

    def load_ops_from_specs(self, specs):
        all_ops = []
        for spec in specs:
            #try:
            parser = API(spec)
            ops = parser.metadata['operations']
            # all_ops = [*all_ops, *ops]
            all_ops.extend(ops)
            #except Exception as e:
            #    print(e)
        return all_ops

    @abstractmethod
    def build(self):
        pass
