import requests
from nose.tools import eq_, ok_
import json
import sys
import os
import re
import unittest

_d = json.loads    # shorthand for json decode
_e = json.dumps    # shorthand for json encode


class SmartAPITest(unittest.TestCase):
    __test__ = True  # explicitly set this to be a test class

    #############################################################
    # Test functions                                            #
    #############################################################

    host = os.getenv("SMARTAPI_HOST", "https://smart-api.info")
    host = host.rstrip('/')
    api = host + '/api'

    ############################################################
    # Helper functions                                          #
    #############################################################

    def truncate(self, s, limit):
        '''truncate a string.'''
        if len(s) <= limit:
            return s
        else:
            return s[:limit] + '...'

    def get_ok(self, url):
        res = requests.get(url)
        assert res.status_code == 200, "status {} != 200 for GET to url: {}".format(
            res.status_code, url)
        return res

    def get_status_code(self, url, status_code):
        res = requests.get(url)
        assert res.status_code == status_code, "status {} != {} for GET to url: {}".format(
            res.status_code, status_code, url)
        return res

    def post_status_code(self, url, params, status_code):
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        res = requests.post(url, data = params, headers=headers)
        assert res.status_code == status_code, "status {} != {} for url: {}\nparams: {}".format(res.status_code, status_code, url, params)
        return res

    def get_404(self, url):
        self.get_status_code(url, 404)

    def get_405(self, url):
        self.get_status_code(url, 405)

    def head_ok(self, url):
        res = requests.head(url)
        assert res.status_code == 200, "status {} != 200 for HEAD to url: {}".format(res.status_code, url)

    def post_ok(self, url, params):
        return self.post_status_code(url, params, 200)

    def query_has_hits(self, q, query_endpoint='query'):
        d = self.json_ok(self.get_ok(
            self.api + '/' + query_endpoint + '?q=' + q))
        assert d.get('total', 0) > 0 and len(d.get('hits', [])) > 0
        return d

    def json_ok(self, s, checkerror=True):
        d = _d(s.text)
        if checkerror:
            assert not (isinstance(d, dict)
                        and 'error' in d), self.truncate(str(d), 100)
        return d

    def setUp(self):
        pass

    def tearDown(self):
        pass

    ############################################################################################
    # Smart API tests
    ############################################################################################

    def test_query_all_has_hits(self):
        self.query_has_hits('__all__')

    def test_query_translator_has_hits(self):
        self.query_has_hits('translator')

    def test_query_by_tags_name_translator_has_hits(self):
        self.query_has_hits('tags.name:translator')

    def test_query_non_exist_special_char_string(self):
        res = self.json_ok(self.get_ok(self.api +
                                       '/query?q=translat\xef\xbf\xbd\xef\xbf\xbd'))
        eq_(res['hits'], [])

    def test_query_string_not_provided(self):
        self.get_status_code(self.api + '/query', 400)

    def test_query_multiple_filters_biothings(self):
        res = self.json_ok(self.get_ok(self.api +
                                       '/query?q=__all__&filters={"tags.name.raw":["annotation","variant"],"info.contact.name.raw":["Chunlei Wu"]}'))
        eq_(len(res['hits']), 3)

    def test_query_specified_fields(self):
        res = self.json_ok(self.get_ok(self.api +
                                       '/query?q=__all__&fields=_id,info'))
        for h in res['hits']:
            self.assertTrue('_id' in h and 'info' in h)

    def test_query_return_raw(self):
        res = self.json_ok(self.get_ok(self.api +
                                       '/query?q=__all__&raw=1'))
        self.assertTrue('_shards' in res)

    def test_query_return_raw_query_match_all(self):
        res = self.json_ok(self.get_ok(self.api +
                                       '/query?q=__all__&rawquery=1'))
        ref_query = {
            "query": {
                "bool": {
                    "must_not": {
                        "term": {
                            "_meta._archived": "true"
                        }
                    },
                    "must": {
                        "match_all": {}
                    }
                }
            }
        }
        self.assertTrue(res == ref_query)

    def test_query_specify_size(self):
        res = self.json_ok(self.get_ok(self.api +
                                       '/query?size=6&q=__all__'))
        eq_(len(res['hits']), 6)

    def test_query_invalid_size(self):
        self.get_status_code(self.api + '/query?q=__all__&size=my', 400)

    # from how does it work
    def test_query_invalid_from(self):
        pass


if __name__ == '__main__':
    unittest.main()
