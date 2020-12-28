'''
    Biothings ESQueryHandler Type Tester
'''
import pytest

from biothings.tests.web import BiothingsTestCase


class DiscoveryQueryTest(BiothingsTestCase):

    def test_all(self):
        '''
        [QUERY] Basic functionality
        '''
        res = self.query(q='__all__')
        assert res['total']['value'] == 1

    def test_query(self):
        '''
        [QUERY] Customization by properties
        '''
        self.query(q='mygene')

