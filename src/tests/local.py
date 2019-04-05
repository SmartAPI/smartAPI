'''
    SmartAPI Read-Only Test
'''


from nose.core import run
from biothings.tests import TornadoTestServerMixin

from remote import SmartAPIRemoteTest


class SmartAPILocalTest(TornadoTestServerMixin, SmartAPIRemoteTest):
    '''
        Self contained test class
        Starts a Tornado server and perform tests against this server.
    '''
    __test__ = True  # explicitly set this to be a test class


if __name__ == '__main__':
    run(argv=['', '--logging-level=INFO', '-v'], defaultTest='local.SmartAPILocalTest')
