import json
from .base_operations_builder import BaseOperationsBuilder
from ..load.sync_loader_factory import sync_loader_factory


class SyncOperationsBuilderWithReasoner(BaseOperationsBuilder):
    _file_path = ''
    _predicates_file_path = ''

    def __init__(self, options, path, predicates_file_path):
        super().__init__(options)
        self._file_path = path
        self._predicates_file_path = predicates_file_path

    def remove_bio_link_prefix(self, _input):
        if not _input:
            return None
        if _input.startswith("biolink:"):
            return _input[8:]
        return _input

    def parse_predicate_endpoint(self, metadata):
        ops = []
        if 'predicates' not in metadata:
            return ops
        for sbj in metadata['predicates']:
            for obj in metadata['predicates'][sbj]:
                if isinstance(metadata['predicates'][sbj][obj], list):
                    for pred in metadata['predicates'][sbj][obj]:
                        ops.append({
                            'association': {
                                'input_type': self.remove_bio_link_prefix(sbj),
                                'output_type': self.remove_bio_link_prefix(obj),
                                'predicate': self.remove_bio_link_prefix(pred),
                                'api_name': metadata['association']['api_name'],
                                'smartapi': metadata['association']['smartapi'],
                                'x-translator': metadata['association']['x-translator'],
                            },
                            'tags': [*metadata['tags'], "bte-trapi"],
                            'query_operation': {
                                'path': '/query',
                                'method': 'post',
                                'server': metadata['query_operation']['server'],
                                'path_params': None,
                                'params': None,
                                'request_body': None,
                                'support_batch': True,
                                'input_separator': ",",
                                'tags': [*metadata['tags'], "bte-trapi"]
                            }
                        })
        if self._options.get('api_names'):
            return [op for op in ops if op['association']['api_name'] in self._options.get('api_names', [])]
        return ops

    def fetch(self):
        with open(self._predicates_file_path) as file:
            data = json.load(file)
            return data

    def build(self):
        specs = sync_loader_factory(
            self._options.get('smart_API_id'),
            self._options.get('team_name'),
            self._options.get('tag'),
            self._options.get('component'),
            self._options.get('api_names'),
            self._file_path,
        )
        nonTRAPIOps = self.load_ops_from_specs(specs)
        predicates_metadata = self.fetch()
        TRAPIOps = []
        for metadata in predicates_metadata:
            TRAPIOps = [*TRAPIOps, *self.parse_predicate_endpoint(metadata)]
        return [*nonTRAPIOps, *TRAPIOps]
