import unittest

from utils.metakg.query_operation import QueryOperationObject


class TestQueryOperationObjectClass(unittest.TestCase):
    def test_missing_fiels_should_return_none(self):
        op = {
            "parameters": {"gene": "{inputs[0]}"},
            "requestBody": {id: "{inputs[1]"},
            "supportBatch": "false",
            "inputs": [{id: "NCBIGene", "semantic": "Gene"}],
            "outputs": [{"id": "NCBIGene", "semantic": "Gene"}],
            "predicate": "related_to",
            "response_mapping": {},
        }

        obj = QueryOperationObject()
        obj.xBTEKGSOperation = op
        self.assertIsNone(obj.input_separator)
