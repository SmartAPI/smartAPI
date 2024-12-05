import unittest
import requests
import json


class TestAPI(unittest.TestCase):
    URL_EXAMPLE = "https://raw.githubusercontent.com/NCATS-Tangerine/translator-api-registry/master/mygene.info/openapi_full.yml"

    def setUp(self):
        self.headers = {"Content-Type": "application/json"}
        with open('/Users/nacosta/Documents/smartAPI/WORKING_BRANCH/add-metakg-endpoint/smartAPI/src/metadata_content.json', 'r') as file:
            self.data = json.load(file)

    # POST Tests
    def test_post_metakg_parse_api_details_1_bte_1(self):
        url = "http://localhost:8000/api/metakg/parse?api_details=1&bte=1"
        response = requests.post(url, headers=self.headers, json=self.data)
        json_response = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertIn('api', json_response['hits'][0].keys())
        self.assertIn('bte', json_response['hits'][0].keys())

    def test_post_metakg_parse_api_details_0_bte_1(self):
        url = "http://localhost:8000/api/metakg/parse?api_details=0&bte=1"
        response = requests.post(url, headers=self.headers, json=self.data)
        json_response = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertIn('bte', json_response['hits'][0].keys())

    def test_post_metakg_parse_api_details_1_bte_0(self):
        url = "http://localhost:8000/api/metakg/parse?api_details=1&bte=0"
        response = requests.post(url, headers=self.headers, json=self.data)
        json_response = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertIn('api', json_response['hits'][0].keys())
        self.assertNotIn('bte', json_response['hits'][0].keys())

    def test_post_metakg_parse_api_details_0_bte_0(self):
        url = "http://localhost:8000/api/metakg/parse?api_details=0&bte=0"
        response = requests.post(url, headers=self.headers, json=self.data)
        json_response = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('bte', json_response['hits'][0].keys())
        self.assertIn('subject', json_response['hits'][0].keys())

    # GET Tests
    def test_get_metakg_parse_api_details_1_bte_1(self):
        url = f"http://localhost:8000/api/metakg/parse?url={self.URL_EXAMPLE}&api_details=1&bte=1"
        response = requests.get(url)
        json_response = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertIn('api', json_response['hits'][0].keys())
        self.assertIn('bte', json_response['hits'][0].keys())

    def test_get_metakg_parse_api_details_0_bte_1(self):
        url = f"http://localhost:8000/api/metakg/parse?url={self.URL_EXAMPLE}&api_details=0&bte=1"
        response = requests.get(url)
        json_response = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertIn('bte', json_response['hits'][0].keys())

    def test_get_metakg_parse_api_details_1_bte_0(self):
        url = f"http://localhost:8000/api/metakg/parse?url={self.URL_EXAMPLE}&api_details=1&bte=0"
        response = requests.get(url)
        json_response = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertIn('api', json_response['hits'][0].keys())
        self.assertNotIn('bte', json_response['hits'][0].keys())

    def test_get_metakg_parse_api_details_0_bte_0(self):
        url = f"http://localhost:8000/api/metakg/parse?url={self.URL_EXAMPLE}&api_details=0&bte=0"
        response = requests.get(url)
        json_response = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('bte', json_response['hits'][0].keys())
        self.assertIn('subject', json_response['hits'][0].keys())


if __name__ == "__main__":
    unittest.main()
