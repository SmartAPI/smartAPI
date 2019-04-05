'''
    SmartAPI Read-Only Test
'''

import os

from nose.core import runmodule
from nose.tools import eq_

from biothings.tests import BiothingsTestCase


class SmartAPIRemoteTest(BiothingsTestCase):

    ''' Test against server specified in environment variable SMARTAPI_HOST
        or SmartAPI production server if SMARTAPI_HOST is not specified '''

    __test__ = True  # explicitly set this to be a test class

    host = os.getenv("SMARTAPI_HOST", "https://smart-api.info")
    api = '/api'

    # Query Functionalities

    def test_101_regular(self):
        ''' Query regular string '''
        self.query(q='translator')

    def test_102_named_field(self):
        ''' Query named field '''
        self.query(q='tags.name:translator')

    def test_103_match_all(self):
        ''' Query all documents '''
        self.query(q='__all__')

    def test_104_random_score(self):
        ''' Query random documents '''
        res = self.query(q='__any__')
        query_1_id = res['hits'][0]['_id']
        res = self.query(q='__any__')
        query_2_id = res['hits'][0]['_id']
        assert query_1_id != query_2_id

    def test_105_filters(self):
        ''' Query with multiple filters '''
        flt = '{"tags.name.raw":["annotation","variant"],"info.contact.name.raw":["Chunlei Wu"]}'
        res = self.query(q='__all__', filters=flt)
        eq_(len(res['hits']), 3)

    # Result Formatting

    def test_201_sources(self):
        ''' Return specified fields '''
        res = self.query(q='__all__', fields='_id,info')
        for hit in res['hits']:
            assert '_id' in hit and 'info' in hit
            assert '_meta' not in hit

    def test_202_size(self):
        ''' Return specified size '''
        res = self.query(q='__all__', size=6)
        eq_(len(res['hits']), 6)

    def test_203_raw(self):
        ''' Return raw ES result '''
        res = self.query(q='__all__', raw=1)
        assert '_shards' in res

    def test_204_query(self):
        ''' Return query sent to ES '''
        res = self.request('query?q=__all__&rawquery=1').json()
        assert "query" in res
        assert "bool" in res["query"]

    # Error Handling

    def test_301_special_char(self):
        ''' Handle special characters '''
        self.query(q='translat\xef\xbf\xbd\xef\xbf\xbd', expect_hits=False)
        self.request("query?q=http://example.com/", expect_status=400)

    def test_302_missing_term(self):
        ''' Handle empty request '''
        self.request("query", expect_status=400)

    def test_303_bad_size(self):
        ''' Handle type error '''
        self.request("query?q=__all__&size=my", expect_status=400)

    def test_304_bad_index(self):
        ''' Handle index out of bound '''
        res_0 = self.request('query?q=__all__&fields=_id&size=5').json()
        ids_0 = {hit['_id'] for hit in res_0['hits']}
        res_1 = self.request('query?q=__all__&fields=_id&size=5&from=5').json()
        ids_1 = [hit['_id'] for hit in res_1['hits']]
        for _id in ids_1:
            if _id in ids_0:
                assert False


if __name__ == '__main__':
    runmodule(argv=['', '--logging-level=INFO', '-v'])
