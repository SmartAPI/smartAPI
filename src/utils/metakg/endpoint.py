import re
from operator import itemgetter

from .query_operation import QueryOperationObject


class Endpoint:
    path_item_object = {}
    api_meta_data = {}
    path = ""
    remove_biolink = False  # flag to remove biolink prefix from semantic types

    def __init__(self, path_item_object, api_meta_data, path):
        self.path_item_object = path_item_object
        self.api_meta_data = api_meta_data
        self.path = path

    def fetch_path_params(self, operation_object):
        params = []
        if "parameters" not in operation_object:
            return params
        for param in operation_object["parameters"]:
            if param.get("in") == "path":
                params.append(param.get("name"))
        return params

    def construct_query_operation(self, data):
        op, method, path_params = itemgetter("op", "method", "path_params")(data)
        server = self.api_meta_data["url"]
        query_operation = QueryOperationObject()
        query_operation.xBTEKGSOperation = op
        query_operation.method = method
        query_operation.path_params = path_params
        query_operation.server = server
        query_operation.path = self.path
        query_operation.tags = self.api_meta_data["tags"]
        return query_operation

    def remove_bio_link_prefix(self, _input):
        if not _input:
            return _input
        if _input.startswith("biolink:"):
            return re.sub(r"biolink:", "", _input)
        return _input

    def resolve_ref_if_provided(self, rec):
        if rec and "$ref" in rec:
            return self.api_meta_data.get("components").fetch_component_by_ref(rec["$ref"])
        return rec

    def construct_association(self, input, output, op):
        return {
            "input_id": self.remove_bio_link_prefix(input["id"]) if self.remove_biolink else input["id"],
            "input_type": self.remove_bio_link_prefix(input["semantic"]) if self.remove_biolink else input["semantic"],
            "output_id": self.remove_bio_link_prefix(output["id"]) if self.remove_biolink else output["id"],
            "output_type": self.remove_bio_link_prefix(output["semantic"]) if self.remove_biolink else output["semantic"],
            "predicate": self.remove_bio_link_prefix(op["predicate"]) if self.remove_biolink else op["predicate"],
            "source": op.get("source"),
            "api_name": self.api_meta_data.get("title"),
            "smartapi": self.api_meta_data.get("smartapi"),
            "x-translator": self.api_meta_data.get("x-translator"),
        }

    def construct_response_mapping(self, op):
        if "responseMapping" in op:
            op["response_mapping"] = op["responseMapping"]

        return {f"{op['predicate']}": self.resolve_ref_if_provided(op.get("response_mapping"))}

    def parse_individual_operation(self, op, method, path_params):
        res = []
        query_operation = self.construct_query_operation({"op": op, "method": method, "path_params": path_params})
        response_mapping = self.construct_response_mapping(op)
        for input in op["inputs"]:
            for output in op["outputs"]:
                association = self.construct_association(input, output, op)
                update_info = {
                    "query_operation": query_operation.to_dict(),
                    "association": association,
                    "response_mapping": response_mapping,
                    "tags": query_operation.tags,
                }
                res.append(update_info)
        return res

    def construct_endpoint_info(self):
        res = []
        for method in ["get", "post"]:
            if method in self.path_item_object:
                path_params = self.fetch_path_params(self.path_item_object[method])
                if "x-bte-kgs-operations" in self.path_item_object[method] and isinstance(
                    self.path_item_object[method]["x-bte-kgs-operations"], list
                ):
                    for rec in self.path_item_object[method]["x-bte-kgs-operations"]:
                        operation = self.resolve_ref_if_provided(rec)
                        operation = operation if isinstance(operation, list) else [operation]
                        for op in operation:
                            if not isinstance(op, dict):
                                continue
                            res = [
                                *res,
                                *self.parse_individual_operation(op, method, path_params),
                            ]
        return res
