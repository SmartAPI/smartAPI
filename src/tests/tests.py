import httplib2
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse
try:
    from urllib.parse import quote_plus
except ImportError:
    from urllib import quote_plus
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

    host = os.getenv("SMARTAPI_HOST","https://smart-api.info")
    host = host.rstrip('/')
    api = host + '/api'
    h = httplib2.Http()

    ############################################################
    # Helper functions                                          #
    #############################################################
    def encode_dict(self, d):
        '''urllib.urlencode (python 2.x) cannot take unicode string.
           encode as utf-8 first to get it around.
        '''
        if PY3:
            # no need to do anything
            return d
        else:
            def smart_encode(s):
                return s.encode('utf-8') if isinstance(s, unicode) else s   # noqa

            return dict([(key, smart_encode(val)) for key, val in d.items()])

    def truncate(self, s, limit):
        '''truncate a string.'''
        if len(s) <= limit:
            return s
        else:
            return s[:limit] + '...'

    def get_ok(self, url):
        res, con = self.h.request((url))
        assert res.status == 200, "status {} != 200 for GET to url: {}".format(res.status, url)
        return con

    def get_status_code(self, url, status_code):
        res, con = self.h.request((url))
        assert res.status == status_code, "status {} != {} for GET to url: {}".format(res.status, status_code, url)

    def post_status_code(self, url, params, status_code):
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        res, con = self.h.request(url, 'POST', urlencode(self.encode_dict(params)), headers=headers)
        assert res.status == status_code, "status {} != {} for url: {}\nparams: {}".format(res.status, status_code, url, params)
        #return con

    def get_404(self, url):
        res, con = self.h.request((url))
        assert res.status == 404, "status {} != 404 for GET to url: {}".format(res.status, url)

    def get_405(self, url):
        res, con = self.h.request((url))
        assert res.status == 405, "status {} != 405 for GET to url: {}".format(res.status, url)

    def head_ok(self, url):
        res, con = self.h.request((url), 'HEAD')
        assert res.status == 200, "status {} != 200 for HEAD to url: {}".format(res.status, url)

    def post_ok(self, url, params):
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        res, con = self.h.request(url, 'POST', urlencode(self.encode_dict(params)), headers=headers)
        assert res.status == 200, "status {} != 200 for url: {}\nparams: {}".format(res.status, url, params)
        return con

    def query_has_hits(self, q, query_endpoint='query'):
        d = self.json_ok(self.get_ok(self.api + '/' + query_endpoint + '?q=' + q))
        assert d.get('total', 0) > 0 and len(d.get('hits', [])) > 0
        return d

    def json_ok(self, s, checkerror=True):
        d = _d(s.decode('utf-8'))
        if checkerror:
            assert not (isinstance(d, dict) and 'error' in d), self.truncate(str(d), 100)
        return d

    def setUp(self):
        pass

    def tearDown(self):
        pass

    ############################################################################################
    # Smart API tests
    ############################################################################################
    
    def test_query(self):
        self.query_has_hits('__all__')
        self.query_has_hits('translator')

        # fielded query
        self.query_has_hits('tags.name:translator')

        res = self.json_ok(self.get_ok(self.api +
                           '/query?q=translat\xef\xbf\xbd\xef\xbf\xbd'))
        eq_(res['hits'], [])

if __name__ == '__main__':
    unittest.main() 
