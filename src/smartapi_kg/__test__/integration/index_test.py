import unittest
import os

from ...metakg import MetaKG
from ...exceptions.fail_to_load_spec import FailToLoadSpecError


class TestConstructMetaKG(unittest.TestCase):
    def test_construct_meta_kg_with_default_parameters(self):
        meta_kg = MetaKG()
        meta_kg.construct_MetaKG()
        self.assertIsInstance(meta_kg.ops, list)
        self.assertGreater(len([op for op in meta_kg.ops if op['association']['api_name'] == 'MyGene.info API']), 0)

    def test_construct_meta_kg_without_options(self):
        meta_kg = MetaKG()
        meta_kg.construct_MetaKG(False, {})
        self.assertIsInstance(meta_kg.ops, list)
        self.assertGreater(len([op for op in meta_kg.ops if op['association']['api_name'] == 'MyGene.info API']), 0)

    def test_construct_meta_kg_based_on_team_name(self):
        meta_kg = MetaKG()
        meta_kg.construct_MetaKG(False, {'team_name': 'Text Mining Provider'})
        self.assertIsInstance(meta_kg.ops, list)
        self.assertGreater(len(meta_kg.ops), 0)
        self.assertIn('Text Mining Provider', meta_kg.ops[0]['association']['x-translator']['team'])

    def test_filter_function(self):
        meta_kg = MetaKG()
        meta_kg.construct_MetaKG(False, {'team_name': 'Text Mining Provider'})
        res = meta_kg.filter({'input_type': 'Disease'})
        self.assertGreater(len(res), 0)
        self.assertEqual(len([op for op in res if op['association']['input_type'] == 'Disease']), len(res))

    def test_construct_meta_kg_with_tag_equal_to_biothings(self):
        meta_kg = MetaKG()
        meta_kg.construct_MetaKG(False, {'tag': 'biothings'})
        self.assertIsInstance(meta_kg.ops, list)
        self.assertGreater(len(meta_kg.ops), 0)
        self.assertIn('biothings', meta_kg.ops[0]['tags'])

    def test_construct_meta_kg_with_non_existing_tag(self):
        meta_kg = MetaKG()
        meta_kg.construct_MetaKG(False, {'tag': 'asdasdflsfd,'})
        self.assertIsInstance(meta_kg.ops, list)
        self.assertEqual(len(meta_kg.ops), 0)

    def test_construct_meta_kg_with_invalid_smartapi_id_should_throw_error(self):
        meta_kg = MetaKG()
        with self.assertRaises(FailToLoadSpecError):
            meta_kg.construct_MetaKG(False, {'smart_API_id': 'invalid'})

    def test_construct_meta_kg_with_smartapi_id(self):
        meta_kg = MetaKG()
        meta_kg.construct_MetaKG(False, {'smart_API_id': '671b45c0301c8624abbd26ae78449ca2'})
        self.assertIsInstance(meta_kg.ops, list)
        self.assertGreater(len(meta_kg.ops), 0)
        self.assertEqual(meta_kg.ops[0]['association']['smartapi']['id'], '671b45c0301c8624abbd26ae78449ca2')
        self.assertEqual(meta_kg.ops[0]['association']['api_name'], 'MyDisease.info API')

    def test_construct_meta_kg_with_component_name(self):
        meta_kg = MetaKG()
        meta_kg.construct_MetaKG(False, {'component': 'KP'})
        self.assertIsInstance(meta_kg.ops, list)
        self.assertGreater(len(meta_kg.ops), 0)
        self.assertEqual(meta_kg.ops[0]['association']['x-translator']['component'], 'KP')
        self.assertEqual(meta_kg.ops[4]['association']['x-translator']['component'], 'KP')

    def test_construct_meta_kg_including_reasoner_tags(self):
        meta_kg = MetaKG()
        meta_kg.construct_MetaKG(True, {'smart_API_id': '912372f46127b79fb387cd2397203709'})
        self.assertIsInstance(meta_kg.ops, list)
        self.assertGreater(len(meta_kg.ops), 0)
        self.assertEqual(meta_kg.ops[0]['association']['input_type'], 'ChemicalSubstance')
        reasoner_ops = [op for op in meta_kg.ops if 'bte-trapi' in op['tags']]
        for op in reasoner_ops:
            self.assertEqual(op['query_operation']['path'], '/query')
            self.assertEqual(op['query_operation']['method'], 'post')

    # ssl.SSLCertVerificationError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self signed certificate
    # happens when GETting this endpoint 'https://openpredict.semanticscience.org/predicates'
    # patched it by doing insecure requests anyways
    def test_construct_meta_kg_including_reasoner_tags_with_no_restrictions(self):
        meta_kg = MetaKG()
        meta_kg.construct_MetaKG(True, {})
        self.assertIsInstance(meta_kg.ops, list)
        self.assertGreater(len(meta_kg.ops), 0)


class TestConstructMetaKGFromLocal(unittest.TestCase):
    def test_construct_meta_kg_from_local_file_successful(self):

        file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'data', 'smartapi_multiomics_kp_query.json'))
        meta_kg = MetaKG(file_path)
        meta_kg.construct_MetaKG(False, {})
        self.assertIsInstance(meta_kg.ops, list)
        self.assertGreater(len(meta_kg.ops), 0)

    def test_construct_meta_kg_from_local_file_path_not_from_query(self):

        file_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'data', 'mygene.json'))
        meta_kg = MetaKG(file_path)
        meta_kg.construct_MetaKG(False, {})
        self.assertIsInstance(meta_kg.ops, list)
        self.assertGreater(len(meta_kg.ops), 0)

    def test_construct_meta_kg_from_default_file(self):
        meta_kg = MetaKG()
        meta_kg.construct_MetaKG(False, {})
        self.assertIsInstance(meta_kg.ops, list)
        self.assertGreater(len(meta_kg.ops), 0)

    def test_construct_meta_kg_with_default_parameters(self):
        meta_kg = MetaKG()
        meta_kg.construct_MetaKG()
        self.assertIsInstance(meta_kg.ops, list)
        self.assertGreater(len(meta_kg.ops), 0)

    def test_construct_meta_kg_sync_including_reasoner(self):
        meta_kg = MetaKG()
        meta_kg.construct_MetaKG_sync(True)
        self.assertIsInstance(meta_kg.ops, list)
        res = [op for op in meta_kg.ops if 'input_id' not in op['association']]
        self.assertGreater(len(res), 100)

    def test_construct_meta_kg_with_tag_equal_to_biothings(self):
        meta_kg = MetaKG()
        meta_kg.construct_MetaKG_sync(False, {'tag': 'biothings'})
        self.assertIsInstance(meta_kg.ops, list)
        self.assertGreater(len(meta_kg.ops), 0) # FAILS HERE
        self.assertIn('biothings', meta_kg.ops[0]['tags'])

    def test_construct_meta_kg_with_team_equal_to_text_mining_provider(self):
        meta_kg = MetaKG()
        meta_kg.construct_MetaKG_sync(False, {'team_name': 'Text Mining Provider'})
        self.assertIsInstance(meta_kg.ops, list)
        self.assertGreater(len(meta_kg.ops), 0)
        self.assertIn('Text Mining Provider', meta_kg.ops[0]['association']['x-translator']['team'])

    def test_construct_meta_kg_smartapi_id(self):
        meta_kg = MetaKG()
        meta_kg.construct_MetaKG_sync(False, {'smart_API_id': '671b45c0301c8624abbd26ae78449ca2'})
        self.assertIsInstance(meta_kg.ops, list)
        self.assertGreater(len(meta_kg.ops), 0)
        self.assertEqual(meta_kg.ops[0]['association']['smartapi']['id'], '671b45c0301c8624abbd26ae78449ca2')
        self.assertEqual(meta_kg.ops[0]['association']['api_name'], 'MyDisease.info API')

    def test_construct_meta_kg_with_component_name(self):
        meta_kg = MetaKG()
        meta_kg.construct_MetaKG_sync(False, {'component': 'KP'})
        self.assertIsInstance(meta_kg.ops, list)
        self.assertGreater(len(meta_kg.ops), 0)
        self.assertEqual(meta_kg.ops[0]['association']['x-translator']['component'], 'KP')
        self.assertEqual(meta_kg.ops[4]['association']['x-translator']['component'], 'KP')

    def test_construct_meta_kg_with_a_constrained_list_of_apis(self):
        meta_kg = MetaKG()
        meta_kg.construct_MetaKG_sync(False, {'api_names': ["MyGene.info API", "MyVariant.info API"]})
        self.assertIsInstance(meta_kg.ops, list)
        self.assertGreater(len(meta_kg.ops), 0)
        apis = [op['association']['api_name'] for op in meta_kg.ops]
        apis = set(apis)
        self.assertEqual(len(apis), 2)
        self.assertIn('MyGene.info API', apis)
        self.assertIn('MyVariant.info API', apis)

    def test_construct_meta_kg_with_a_constrained_list_of_apis_and_enable_reasoner(self):
        meta_kg = MetaKG()
        meta_kg.construct_MetaKG_sync(True, {'api_names': ["MyGene.info API", "MyVariant.info API", "Automat HMDB"]})
        self.assertIsInstance(meta_kg.ops, list)
        self.assertGreater(len(meta_kg.ops), 0)
        apis = [op['association']['api_name'] for op in meta_kg.ops]
        apis = set(apis)
        self.assertEqual(len(apis), 3)
        self.assertIn('MyGene.info API', apis)
        self.assertIn('MyVariant.info API', apis)
        self.assertIn('Automat HMDB', apis)


if __name__ == '__main__':
    unittest.main()
