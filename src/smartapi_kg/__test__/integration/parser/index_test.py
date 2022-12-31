import json
import os
import unittest
from smartapi_kg.parser.index import API


class TestAPIParser(unittest.TestCase):
    def setUp(self):
        with open(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'data', 'mygene.json')), encoding='utf-8') as f:
            mygene_doc = json.load(f)
            mygene = API(mygene_doc)
            self.metadata = mygene.metadata

    def test_parse_API_name(self):
        self.assertEqual(self.metadata['title'], 'MyGene.info API')

    def test_parse_API_tags(self):
        self.assertIn('biothings' ,self.metadata['tags'])

    def test_parse_component(self):
        self.assertIsNotNone(self.metadata['components'])

    def test_fetch_meta_data(self):
        self.assertEqual(self.metadata['title'], 'MyGene.info API')
        self.assertIn('biothings', self.metadata['tags'])
        self.assertEqual(self.metadata['url'], 'https://mygene.info/v3')
        self.assertIsNotNone(self.metadata['components'])

    def test_fetch_all_operations(self):
        ops = self.metadata['operations']
        self.assertEqual(ops[0]['association']['api_name'], 'MyGene.info API')


class TestAPIParserWhichIsAlreadyDereferenced(unittest.TestCase):
    def setUp(self):

        with open(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'data', 'opentarget.json')), encoding='utf-8') as f:
            smartapi_spec = json.load(f)
            opentarget = API(smartapi_spec)
            self.metadata = opentarget.metadata

    def test_parse_component(self):
        self.assertEqual(self.metadata['components'], None)

    def test_fetch_meta_data(self):
        self.assertEqual(self.metadata['title'], 'OpenTarget API')
        self.assertIn('translator', self.metadata['tags'])
        self.assertEqual(self.metadata['url'], 'https://platform-api.opentargets.io/v3')
        self.assertEqual(self.metadata['components'], None)

    # Fail
    # AssertionError: 'biolink:related_to' != 'related_to'
    def test_fetch_all_operations(self):
        ops = self.metadata['operations']
        self.assertEqual(ops[0]['association'].get('api_name'), 'OpenTarget API')
        self.assertEqual(ops[0]['association'].get('predicate'), 'related_to')
        self.assertEqual(ops[0]['association'].get('input_id'), 'ENSEMBL')
        self.assertEqual(ops[0]['query_operation'].path, '/platform/public/evidence/filter')


class TestAPIParserUsingSpecsWithParameters(unittest.TestCase):
    def test_path_params(self):

        with open(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'data', 'litvar.json')), encoding='utf-8') as f:
            smartapi_spec = json.load(f)
            litvar = API(smartapi_spec)
            path_params = litvar.metadata['operations'][0]['query_operation'].path_params
            self.assertEqual(path_params, ['variantid'])
