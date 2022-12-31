import logging
import requests
import json
# from urllib3.exceptions import ResponseNotChunked
from .async_operations_builder import AsyncOperationsBuilder
from ..parser.index import API


logger = logging.getLogger(__name__.split('.')[-1])


class AsyncOperationsBuilderWithReasoner(AsyncOperationsBuilder):
    timeout = 60      # timeout when calling /meta_knowledge_graph endpoint
    remove_biolink = False      # flag to remove biolink prefix in subject/object/predicate

    def get_TRAPI_with_metakg_endpoint(self, specs):
        trapi = []
        for spec in specs:
            #try:
            parser = API(spec)
            metadata = parser.metadata
            _paths = metadata.get('paths', {})
            if "/meta_knowledge_graph" in _paths and "/query" in _paths and metadata.get("x-translator", {}).get('team'):
                trapi.append(metadata)
            #except Exception as e:
            #    pass
        logger.info(f"Found {len(trapi)} TRAPI APIs.")
        return trapi

    def construct_query_url(self, server_url):
        if server_url.endswith('/'):
            server_url = server_url[:-1]
        return server_url + "/meta_knowledge_graph"

    def remove_bio_link_prefix(self, _input):
        if not isinstance(_input, str):
            return None
        if _input.startswith('biolink:'):
            return _input[8:]
        return _input

    def parse_trapi_metakg_endpoint(self, response, metadata):
        ops = []
        for pred in response.get('edges', []):
            ops.append({
                'association': {
                    'input_type': self.remove_bio_link_prefix(pred['subject']) if self.remove_biolink else pred['subject'],
                    'output_type': self.remove_bio_link_prefix(pred['object']) if self.remove_biolink else pred['object'],
                    'predicate': self.remove_bio_link_prefix(pred['predicate']) if self.remove_biolink else pred['predicate'],
                    'api_name': metadata.get('title'),
                    'smartapi': metadata.get('smartapi'),
                    'x-translator': metadata.get('x-translator'),
                },
                'tags': [*metadata.get('tags'), 'bte-trapi'],
                'query_operation': {
                    'path': '/query',
                    'method': 'post',
                    'server': metadata.get('url'),
                    'path_params': None,
                    'params': None,
                    'request_body': None,
                    'support_batch': True,
                    'input_separator': ',',
                    'tags': [*metadata.get('tags'), 'bte-trapi']
                }
            })
        return ops

    def _get_url(self, url, extra_log_msg=''):
        logger.info(f'Fetching "{url}" {extra_log_msg}...')
        data = {}
        # sometimes the request is in chunked mode but we can't know beforehand
        # so we expect chunks first, if that fails fallback to regular get request
        try:
            # Using verify=False to bypass SSL: CERTIFICATE_VERIFY_FAILED error on some specific requests
            #     with requests.get(self.construct_query_url(url), stream=True, verify=True, timeout=self.timeout) as response:
            #         if response.status_code == 200:
            #             data_str = ''
            #             for chunk in (response.raw.read_chunked()):
            #                 data_str = data_str + chunk.decode("UTF-8")
            #             data = json.loads(data_str)
            # except ResponseNotChunked:
            response = requests.get(self.construct_query_url(url), verify=True, timeout=self.timeout)
            data = response.json()
        except requests.ReadTimeout:
            logger.error("Skipped [Timeout]")
            err = "ReadTimeout"
            if err in self.metakg_errors:
                self.metakg_errors[err].append(url)
            else:
                self.metakg_errors[err] = [url]
        except Exception as e:
            err = repr(e)
            logger.error(f"Skipped [{err}]")
            if err in self.metakg_errors:
                self.metakg_errors[err].append(url)
            else:
                self.metakg_errors[err] = [url]
        logger.info(f"Done [{len(data.get('nodes', []))}, {len(data.get('edges', []))}]")
        return data

    def get_ops_from_metakg_endpoint(self, metadata, extra_log_msg=""):
        if metadata.get('url'):
            data = self._get_url(metadata['url'], extra_log_msg=extra_log_msg)
            return self.parse_trapi_metakg_endpoint(data, metadata)
        else:
            return []

    def get_ops_from_metakg_endpoints(self, specs):
        metadata_list = self.get_TRAPI_with_metakg_endpoint(specs)
        res = []
        cnt_metadata_list = len(metadata_list)
        self.metakg_errors = {}
        for i, metadata in enumerate(metadata_list):
            res.extend(self.get_ops_from_metakg_endpoint(metadata, f"[{i+1}/{cnt_metadata_list}]"))
        if self.metakg_errors:
            cnt_metakg_errors = sum([len(x) for x in self.metakg_errors.values()])
            logger.error(f"Found {cnt_metakg_errors} TRAPI metakg errors:\n {json.dumps(self.metakg_errors, indent=2)}")
        return res

    def build(self):
        specs = self.load()
        non_TRAPI_ops = self.load_ops_from_specs(specs)
        TRAPI_ops = self.get_ops_from_metakg_endpoints(specs)
        return non_TRAPI_ops + TRAPI_ops
