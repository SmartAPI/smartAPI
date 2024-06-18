"""
MetaKG Index Testing
"""

from biothings.tests.web import BiothingsWebAppTest

from admin import refresh_metakg, consolidate_metakg, refresh_has_metakg

# setup fixture
@pytest.fixture(autouse=True, scope="module")
def setup_fixture():
    reset()
    # refresh index
    refresh()
    
    refresh_metakg()
    consolidate_metakg()
    refresh_has_metakg()    

class TestMetaKGEndpoint(BiothingsWebAppTest):
    def test_metakg_endpoint(self):
        """
        GET /api/metakg/?q=*
        {
            "took": 1,
            "total": 27527,
            "max_score": 1,
            "hits": [
            {
                "_id": "SmallMolecule-positively_correlated_with-Drug",
                "_score": 1,
                "api": [
                    {
                    "name": "Automat-icees-kg(Trapi v1.4.0)",
                    "smartapi": {
                    "id": "76a164ff43e7ab39a5b98a782f6361bf"
                }
            },
                {
                    "name": "Automat-robokop(Trapi v1.5.0)",
                    "smartapi": {
                    "id": "4f9c8853b721ef1f14ecee6d92fc19b5"
                }
            }....
        }
        """
        response = self.get("/api/metakg/?q=*")
        self.assertEqual(response.code, 200)  # check that the status code is 200
        # Add more assertions to check the response body

    def test_metakg_endpoint_subject(self):
        response = self.get("/api/metakg/?subject=Virus")
        self.assertEqual(response.code, 200)
        data = response.json()
        self.assertIn('subject', data)
        self.assertEqual(data['subject'], 'Virus')

    def test_metakg_endpoint_object(self):
        response = self.get("/api/metakg/?object=Drug")
        self.assertEqual(response.code, 200)
        data = response.json()
        self.assertIn('object', data)
        self.assertEqual(data['object'], 'Drug')

    def test_metakg_endpoint_node(self):
        response = self.get("/api/metakg/?node=Virus")
        self.assertEqual(response.code, 200)
        data = response.json()
        self.assertIn('node', data)
        self.assertEqual(data['node'], 'Virus')

    def test_metakg_endpoint_predicate(self):
        response = self.get("/api/metakg/?predicate=associated")
        self.assertEqual(response.code, 200)
        data = response.json()
        self.assertIn('predicate', data)
        self.assertEqual(data['predicate'], 'associated')

    def test_metakg_endpoint_size(self):
        response = self.get("/api/metakg/?size=100")
        self.assertEqual(response.code, 200)
        data = response.json()
        self.assertIn('size', data)
        self.assertEqual(data['size'], 100)

    def test_metakg_endpoint_download(self):
        response = self.get("/api/metakg/?download=true")
        self.assertEqual(response.code, 200)
        data = response.json()
        self.assertIn('download', data)
        self.assertTrue(data['download'])

    def test_metakg_endpoint_expand(self):
        response = self.get("/api/metakg/?expand=subject")
        self.assertEqual(response.code, 200)
        data = response.json()
        self.assertIn('expand', data)
        self.assertEqual(data['expand'], 'subject')

    def test_metakg_endpoint_default_view(self):
        response = self.get("/api/metakg/?default_view=json")
        self.assertEqual(response.code, 200)
        data = response.json()
        self.assertIn('default_view', data)
        self.assertEqual(data['default_view'], 'json')

    def test_metakg_endpoint_header(self):
        response = self.get("/api/metakg/?header=true")
        self.assertEqual(response.code, 200)
        data = response.json()
        self.assertIn('header', data)
        self.assertTrue(data['header'])

    def test_metakg_endpoint_consolidated(self):
        response = self.get("/api/metakg/?consolidated=true")
        self.assertEqual(response.code, 200)
        data = response.json()
        self.assertIn('consolidated', data)
        self.assertTrue(data['consolidated'])

    def test_metakg_endpoint_api_details(self):
        response = self.get("/api/metakg/?api_details=true")
        self.assertEqual(response.code, 200)
        data = response.json()
        self.assertIn('api_details', data)
        self.assertTrue(data['api_details'])

    def test_metakg_endpoint_bte(self):
        response = self.get("/api/metakg/?bte=true")
        self.assertEqual(response.code, 200)
        data = response.json()
        self.assertIn('bte', data)
        self.assertTrue(data['bte'])
