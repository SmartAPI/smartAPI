''' SmartAPI Data-Aware Tests
    nosetests tests:SmartAPITest
    nosetests tests:SmartAPITestTornadoClient
'''

import json
import os
import re
import sys
import unittest
import nose
import requests
from nose.tools import eq_, ok_
from tornado.web import Application

from biothings.tests.test_helper import (BiothingsTestCase,
                                         TornadoTestServerMixin)
from biothings.web.settings import BiothingESWebSettings


class SmartAPITest(BiothingsTestCase):

    host = os.getenv("SMARTAPI_HOST", "https://smart-api.info")
    host = host.rstrip('/')
    api = host + '/api'

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
        self.get_status_match(self.api + '/query', 400)

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
        self.get_status_match(self.api + '/query?q=__all__&size=my', 400)

    def test_query_invalid_from(self):
        res_0 = self.json_ok(self.get_ok(self.api +
                                         '/query?q=__all__&fields=_id&size=5'))
        ids_0 = set([hit['_id'] for hit in res_0['hits']])
        res_1 = self.json_ok(self.get_ok(self.api +
                                         '/query?q=__all__&fields=_id&size=5&from=5'))
        ids_1 = [hit['_id'] for hit in res_1['hits']]
        for _id in ids_1:
            if _id in ids_0:
                self.assertTrue(False)


class SmartAPITestTornadoClient(TornadoTestServerMixin, SmartAPITest):
    '''
        Self contained test class
        Starts a Tornado server and perform tests against this server.
    '''

    @classmethod
    def setup_class(cls):
        ''' Reads Tornado Settings from config.py '''
        cls.WEB_SETTINGS = BiothingESWebSettings(config='config')
        cls.APP_LIST = cls.WEB_SETTINGS.generate_app_list()
        cls.STATIC_PATH = cls.WEB_SETTINGS.STATIC_PATH

    def get_app(self):
        return Application(self.APP_LIST, static_path=self.STATIC_PATH)

# client = SmartAPITestTornadoClient(methodName='test_query_multiple_filters_biothings')
if __name__ == '__main__':
    nose.main()
