import os
import unittest
from unittest import mock

from requests.exceptions import HTTPError

from utils.metakg import MetaKG
from utils.metakg.exceptions.fail_to_load_spec import FailToLoadSpecError


class TestConstructMetaKG(unittest.TestCase):
    smartapi_file_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            os.pardir,
            os.pardir,
            'data',
            'smartapi_multiomics_kp_query.json',
        )
    )
    mygene_file_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            os.pardir,
            os.pardir,
            'data',
            'mygene.json'
        )
    )

    def test_construct_meta_kg(self):
        meta_kg = MetaKG()
        meta_kg.construct_MetaKG()
        self.assertIsInstance(meta_kg.ops, list)
        self.assertGreater(len([op for op in meta_kg.ops if op['association']['api_name'] == 'MyGene.info API']), 0)

    @mock.patch("utils.metakg.loader.requests.get")
    def test_construct_meta_kg_with_invalid_smartapi_id_should_throw_error(self, mock_get):
        mock_get.return_value = mock.Mock(
            status_code=400,
            raise_for_status=mock.Mock(side_effect=HTTPError())
        )
        meta_kg = MetaKG()
        with self.assertRaises(FailToLoadSpecError):
            meta_kg.construct_MetaKG()

    def test_construct_meta_kg_from_local_file_successful(self):
        meta_kg = MetaKG(self.smartapi_file_path)
        meta_kg.construct_MetaKG()
        self.assertIsInstance(meta_kg.ops, list)
        self.assertGreater(len(meta_kg.ops), 0)

    def test_construct_meta_kg_from_local_file_path_not_from_query(self):
        meta_kg = MetaKG(self.mygene_file_path)
        meta_kg.construct_MetaKG()
        self.assertIsInstance(meta_kg.ops, list)
        self.assertGreater(len(meta_kg.ops), 0)
