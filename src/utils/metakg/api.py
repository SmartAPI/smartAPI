from model.smartapi import SmartAPIDoc
from .endpoint import Endpoint
from .component import Components


class API:
    _smartapi_doc = {}

    def __init__(self, smartapi_doc):
        self._smartapi_doc = smartapi_doc

    @property
    def smartapi_doc(self):
        return self._smartapi_doc

    @property
    def metadata(self):
        metadata = self.fetch_API_meta()
        metadata['operations'] = self.fetch_all_opts()
        return metadata

    def fetch_API_title(self):
        if "info" not in self.smartapi_doc:
            return None
        return self.smartapi_doc['info']['title']

    def fetch_XTranslator_component(self):
        if "info" not in self.smartapi_doc:
            return None
        if "x-translator" not in self.smartapi_doc['info']:
            return None
        return self.smartapi_doc['info']["x-translator"]['component']

    def fetch_XTranslator_team(self):
        if "info" not in self.smartapi_doc:
            return []
        if "x-translator" not in self.smartapi_doc['info']:
            return []
        return self.smartapi_doc['info']["x-translator"]['team']

    def fetch_API_tags(self):
        if "tags" not in self.smartapi_doc:
            return None
        return [x['name'] for x in self.smartapi_doc['tags']]

    def fetch_server_url(self):
        if "servers" not in self.smartapi_doc:
            return None
        return SmartAPIDoc.get_default_server_url(self.smartapi_doc['servers'])

    def fetch_components(self):
        if "components" not in self.smartapi_doc:
            return None
        return Components(self.smartapi_doc['components'])

    def fetch_API_meta(self):
        return {
            'title': self.fetch_API_title(),
            'tags': self.fetch_API_tags(),
            'url': self.fetch_server_url(),
            'x-translator': {
                'component': self.fetch_XTranslator_component(),
                'team': self.fetch_XTranslator_team(),
            },
            'smartapi': {
                'id': self.smartapi_doc.get('_id'),
                'meta': self.smartapi_doc.get('_meta'),
            },
            'components': self.fetch_components(),
            'paths': list(self.smartapi_doc['paths'].keys()) if isinstance(self.smartapi_doc.get('paths'), dict) else [],
            'operations': [],
        }

    def fetch_all_opts(self):
        ops = []
        api_meta = self.fetch_API_meta()
        if "paths" in self.smartapi_doc:
            for path in self.smartapi_doc['paths'].keys():
                ep = Endpoint(self.smartapi_doc['paths'][path], api_meta, path)
                ops = [*ops, *ep.construct_endpoint_info()]
        return ops
