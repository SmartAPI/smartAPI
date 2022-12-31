import os

from .operations_builder.async_builder_factory import async_builder_factory
from .operations_builder.sync_builder_factory import sync_builder_factory


class MetaKG:
    _ops = []
    _file_path = ''
    _predicates_path = ''

    def __init__(self, path=None, predicates_path=None):
        self._ops = []
        self.path = path
        self.predicates_path = predicates_path

    @property
    def path(self):
        return self._file_path

    @path.setter
    def path(self, file_path):
        if not file_path:
            directory = os.path.dirname(__file__)
            self._file_path = os.path.join(directory, 'data', 'smartapi_specs.json')
        else:
            self._file_path = file_path

    @property
    def predicates_path(self):
        return self._predicates_path

    @predicates_path.setter
    def predicates_path(self, file_path):
        if not file_path:
            directory = os.path.dirname(__file__)
            self._predicates_path = os.path.join(directory, 'data', 'predicates.json')
        else:
            self._predicates_path = file_path

    @property
    def ops(self):
        return self._ops

    def construct_MetaKG(self, include_reasoner=False, options={}):
        self._ops = async_builder_factory(options, include_reasoner)
        return self._ops

    def construct_MetaKG_sync(self, include_reasoner=False, options={}):
        self._ops = sync_builder_factory(
            options,
            include_reasoner,
            self._file_path,
            self._predicates_path
        )
        return self._ops

    def get_associations(self):
        associations = []
        for op in self.ops:
            associations.append({
                'subject': op['association']['input_type'],
                'object': op['association']['output_type'],
                'predicate': op['association']['predicate'],
                'provided_by': op['association'].get('source'),
                'api': {
                    'name': op['association']['api_name'],
                    'smartapi': {
                        'metadata': op['association']['smartapi']['meta']['url'],
                        'id': op['association']['smartapi']['id'],
                        'ui': "https://smart-api.info/ui/" + op['association']['smartapi']['id']
                    },
                    'x-translator': op['association']['x-translator']
                }
            })
        return associations
