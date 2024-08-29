import json
import logging
from copy import copy
from typing import Union

from model.smartapi import SmartAPIDoc
from utils import decoder
from utils.downloader import download

from .component import Components
from .endpoint import Endpoint

logger = logging.getLogger("metakg_parser")


class API:
    _smartapi_doc = None

    def __init__(self, smartapi_doc: Union[dict, None] = None, url: Union[str, None] = None, id: Union[str, None] = None):
        self._smartapi_doc = smartapi_doc
        self.url = url
        self._id = id
        if self.url and not self._id:
            # generate hashed _id from url
            self._id = decoder.get_id(self.url)

    @property
    def smartapi_doc(self):
        if self._smartapi_doc is None and self.url:
            content = download(self.url)
            if content.status == 200:
                self._smartapi_doc = decoder.to_dict(content.raw)
        return self._smartapi_doc

    @property
    def metadata(self):
        metadata = self.fetch_API_meta()
        metadata["operations"] = self.fetch_all_opts()
        return metadata

    @property
    def is_trapi(self):
        """return True if a TRAPI"""
        return self.has_tags("trapi", "translator")

    def has_tags(self, *tags):
        """return True if an SmartAPI contains all given tags"""
        _tag_set = set(self.tags)
        return len(set(tags) - _tag_set) == 0

    @property
    def title(self):
        if "info" not in self.smartapi_doc:
            return None
        return self.smartapi_doc["info"]["title"]

    def fetch_XTranslator_component(self):
        if "info" not in self.smartapi_doc:
            return None
        if "x-translator" not in self.smartapi_doc["info"]:
            return None
        return self.smartapi_doc["info"]["x-translator"]["component"]

    def fetch_XTranslator_team(self):
        if "info" not in self.smartapi_doc:
            return []
        if "x-translator" not in self.smartapi_doc["info"]:
            return []
        return self.smartapi_doc["info"]["x-translator"]["team"]

    @property
    def tags(self):
        if "tags" not in self.smartapi_doc:
            return []
        return [x["name"] for x in self.smartapi_doc["tags"]]

    @property
    def server_url(self):
        if "servers" not in self.smartapi_doc:
            return None
        _server_url = SmartAPIDoc.get_default_server_url(self.smartapi_doc["servers"])
        if _server_url.endswith("/"):
            _server_url = _server_url[:-1]
        return _server_url

    @property
    def components(self):
        if "components" not in self.smartapi_doc:
            return None
        return Components(self.smartapi_doc["components"])

    def fetch_API_meta(self):
        return {
            "title": self.title,
            "tags": self.tags,
            "url": self.server_url,
            "x-translator": {
                "component": self.fetch_XTranslator_component(),
                "team": self.fetch_XTranslator_team(),
            },
            "smartapi": {
                "id": self.smartapi_doc.get("_id") or self._id,
                "meta": self.smartapi_doc.get("_meta"),
            },
            "components": self.components,
            "paths": list(self.smartapi_doc["paths"].keys())
            if isinstance(self.smartapi_doc.get("paths"), dict)
            else [],
            "operations": [],
        }

    def fetch_all_opts(self):
        ops = []
        api_meta = self.fetch_API_meta()
        if "paths" in self.smartapi_doc:
            for path in self.smartapi_doc["paths"].keys():
                ep = Endpoint(self.smartapi_doc["paths"][path], api_meta, path)
                ops = [*ops, *ep.construct_endpoint_info()]
        return ops

    # methods for extracting metakg edges
    def extract_metakgedges(self, ops, extra_data=None):
        extra_data = extra_data or {}

        metakg_edges = []
        for op in ops:
            smartapi_data = op["association"]["smartapi"]
            url = (smartapi_data.get("meta") or {}).get("url") or extra_data.get("url")
            _id = smartapi_data.get("id") or extra_data.get("id")

            edge = {
                "subject": op["association"]["input_type"],
                "object": op["association"]["output_type"],
                "subject_prefix": op["association"]["input_id"],
                "object_prefix": op["association"]["output_id"],
                "predicate": op["association"]["predicate"],
                "api": {
                    "name": op["association"]["api_name"],
                    "smartapi": {
                        "metadata": url,
                        "id": _id,
                        "ui": f"https://smart-api.info/ui/{_id}",
                    },
                    "tags": op["tags"],
                    "x-translator": op["association"]["x-translator"],
                    "provided_by": op["association"].get("source"),
                    # "date_created": (smartapi_data.get("meta") or {}).get("date_created"),
                    # "date_updated": (smartapi_data.get("meta") or {}).get("date_updated"),
                    # "username": (smartapi_data.get("meta") or {}).get("username"),
                },
            }
            # include bte-specific edge metadata
            bte = {}
            for attr in ["query_operation", "response_mapping"]:
                if attr in op:
                    bte[attr] = op[attr]
                # remove redundant query_operation.tags field
                if attr == "query_operation" and "tags" in bte[attr]:
                    bte[attr] = copy(bte[attr])
                    del bte[attr]["tags"]
            if bte:
                edge["api"]["bte"] = bte
            metakg_edges.append(edge)
        return metakg_edges

    def get_xbte_metaedges(self, extra_data=None):
        mkg = self.extract_metakgedges(self.metadata["operations"], extra_data=extra_data)
        no_nodes = len({x["subject"] for x in mkg} | {x["object"] for x in mkg})
        no_edges = len({x["predicate"] for x in mkg})
        logger.info("Done [%s nodes, %s edges]", no_nodes, no_edges)
        return mkg

    def get_trapi_metaedges(self, extra_data=None):
        ops = []
        self.metakg_errors = {}
        ops.extend(self.get_ops_from_trapi())
        if self.metakg_errors:
            cnt_metakg_errors = sum([len(x) for x in self.metakg_errors.values()])
            logger.error(f"Found {cnt_metakg_errors} TRAPI metakg errors:\n {json.dumps(self.metakg_errors, indent=2)}")

        return self.extract_metakgedges(ops, extra_data=extra_data)

    def get_metakg(self, include_trapi=True):
        self.metakg_errors = None  # reset metakg_errors
        if self.is_trapi:
            metakg = self.get_trapi_metaedges() if include_trapi else []
        else:
            metakg = self.get_xbte_metaedges()
        return metakg

    def get_ops_from_trapi(self):
        if self.metadata.get("url"):
            trapi_metakg_url = self.metadata["url"] + "/meta_knowledge_graph"
            content = download(trapi_metakg_url, timeout=60)   # 60s timeout, as trapi endpoint can be slow
            if content.status == 200:
                data = decoder.to_dict(content.raw)
                return self.parse_trapi_metakg_endpoint(data)
        return []

    def parse_trapi_metakg_endpoint(self, response):
        ops = []
        for pred in response.get("edges", []):
            ops.append(
                {
                    "association": {
                        "input_type": self.remove_bio_link_prefix(pred["subject"]),
                        "input_id": response.get("nodes", {}).get(pred["subject"], {}).get("id_prefixes"),
                        "output_type": self.remove_bio_link_prefix(pred["object"]),
                        "output_id": response.get("nodes", {}).get(pred["object"], {}).get("id_prefixes"),
                        "predicate": self.remove_bio_link_prefix(pred["predicate"]),
                        "api_name": self.metadata.get("title"),
                        "smartapi": self.metadata.get("smartapi"),
                        "x-translator": self.metadata.get("x-translator"),
                    },
                    "tags": [*self.metadata.get("tags"), "bte-trapi"],
                    "query_operation": {
                        "path": "/query",
                        "method": "post",
                        "server": self.metadata.get("url"),
                        "path_params": None,
                        "params": None,
                        "request_body": None,
                        "support_batch": True,
                        "input_separator": ",",
                        "tags": [*self.metadata.get("tags"), "bte-trapi"],
                    },
                }
            )
        return ops

    def remove_bio_link_prefix(self, _input):
        if not isinstance(_input, str):
            return
        if _input.startswith("biolink:"):
            return _input[8:]
        return _input
