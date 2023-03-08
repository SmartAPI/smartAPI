import json
import logging

import requests

from .api import API

logger = logging.getLogger("metakg_parser")


class MetaKGParser:
    get_url_timeout = 60
    metakg_errors = None

    def get_non_TRAPI_metadatas(self, data, extra_data=None):
        parser = API(data)
        mkg = self.extract_metadatas(parser.metadata["operations"], extra_data=extra_data)
        no_nodes = len({x["subject"] for x in mkg} | {x["object"] for x in mkg})
        no_edges = len({x["predicate"] for x in mkg})
        logger.info("Done [%s nodes, %s edges]", no_nodes, no_edges)
        return mkg

    def get_TRAPI_metadatas(self, data, extra_data=None):
        ops = []
        metadata_list = self.get_TRAPI_with_metakg_endpoint(data)
        count_metadata_list = len(metadata_list)
        self.metakg_errors = {}
        for i, metadata in enumerate(metadata_list):
            ops.extend(self.get_ops_from_metakg_endpoint(metadata, f"[{i+1}/{count_metadata_list}]"))
        if self.metakg_errors:
            cnt_metakg_errors = sum([len(x) for x in self.metakg_errors.values()])
            logger.error(f"Found {cnt_metakg_errors} TRAPI metakg errors:\n {json.dumps(self.metakg_errors, indent=2)}")

        return self.extract_metadatas(ops, extra_data=extra_data)

    def get_TRAPI_with_metakg_endpoint(self, data):
        metadatas = []
        parser = API(data)
        metadata = parser.metadata
        _paths = metadata.get("paths", {})
        _team = metadata.get("x-translator", {}).get("team")
        if "/meta_knowledge_graph" in _paths and "/query" in _paths and _team:
            metadatas.append(metadata)
        return metadatas

    def construct_query_url(self, server_url):
        if server_url.endswith("/"):
            server_url = server_url[:-1]
        return server_url + "/meta_knowledge_graph"

    def remove_bio_link_prefix(self, _input):
        if not isinstance(_input, str):
            return
        if _input.startswith("biolink:"):
            return _input[8:]
        return _input

    def parse_trapi_metakg_endpoint(self, response, metadata):
        ops = []
        for pred in response.get("edges", []):
            ops.append(
                {
                    "association": {
                        "input_type": self.remove_bio_link_prefix(pred["subject"]),
                        "output_type": self.remove_bio_link_prefix(pred["object"]),
                        "predicate": self.remove_bio_link_prefix(pred["predicate"]),
                        "api_name": metadata.get("title"),
                        "smartapi": metadata.get("smartapi"),
                        "x-translator": metadata.get("x-translator"),
                    },
                    "tags": [*metadata.get("tags"), "bte-trapi"],
                    "query_operation": {
                        "path": "/query",
                        "method": "post",
                        "server": metadata.get("url"),
                        "path_params": None,
                        "params": None,
                        "request_body": None,
                        "support_batch": True,
                        "input_separator": ",",
                        "tags": [*metadata.get("tags"), "bte-trapi"],
                    },
                }
            )
        return ops

    def get_url(self, url, extra_log_msg=""):
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
            response = requests.get(
                self.construct_query_url(url),
                verify=True,
                timeout=self.get_url_timeout,
            )
            if response.status_code != 200:
                raise Exception("Not Found")
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
        logger.info("Done [%s nodes, %s edges]", len(data.get('nodes', [])), len(data.get('edges', [])))
        return data

    def get_ops_from_metakg_endpoint(self, metadata, extra_log_msg=""):
        if metadata.get("url"):
            data = self.get_url(metadata["url"], extra_log_msg=extra_log_msg)
            return self.parse_trapi_metakg_endpoint(data, metadata)
        return []

    def extract_metadatas(self, ops, extra_data=None):
        extra_data = extra_data or {}

        metadatas = []
        for op in ops:
            smartapi_data = op["association"]["smartapi"]
            url = (smartapi_data.get("meta") or {}).get("url") or extra_data.get("url")
            _id = smartapi_data.get("id") or extra_data.get("id")

            metadatas.append(
                {
                    "subject": op["association"]["input_type"],
                    "object": op["association"]["output_type"],
                    "predicate": op["association"]["predicate"],
                    "provided_by": op["association"].get("source"),
                    "api": {
                        "name": op["association"]["api_name"],
                        "smartapi": {
                            "metadata": url,
                            "id": _id,
                            "ui": f"https://smart-api.info/ui/{_id}",
                        },
                        "x-translator": op["association"]["x-translator"],
                    },
                }
            )
        return metadatas
