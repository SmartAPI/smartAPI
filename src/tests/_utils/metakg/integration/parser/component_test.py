import unittest
import json
import os

from utils.metakg.parser.component import Components


class TestComponent(unittest.TestCase):
    def test_ref_with_trailing_slash(self):
        with open(os.path.abspath(os.path.join(os.path.dirname(__file__), 'components.json'))) as f:
            components = json.load(f)
            cp_obj = Components(components)
            rec = cp_obj.fetch_component_by_ref('#/components/x-bte-kgs-operations/enablesMF/')
            self.assertEqual(rec[0]['source'], 'entrez')

    def test_wrong_ref(self):
        with open(os.path.abspath(os.path.join(os.path.dirname(__file__), 'components.json'))) as f:
            components = json.load(f)
            cp_obj = Components(components)
            rec = cp_obj.fetch_component_by_ref('/components/x-bte-response-mapping')
            self.assertEqual(rec, None)

    def test_wrong_ref_2(self):
        with open(os.path.abspath(os.path.join(os.path.dirname(__file__), 'components.json'))) as f:
            components = json.load(f)
            cp_obj = Components(components)
            rec = cp_obj.fetch_component_by_ref('#/components/x-bte-response-mapping/hello/world')
            self.assertEqual(rec, None)
