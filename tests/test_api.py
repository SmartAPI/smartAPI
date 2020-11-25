# import pytest

from tornado.escape import json_encode
from tornado.web import create_signed_value

from biothings.tests.web import BiothingsTestCase

from ..src.web.api.model.api_doc import API_Doc

class BaseTestCase(BiothingsTestCase):

    @classmethod
    def cookie_header(cls, username):
        cookie_name, cookie_value = 'user', {'login': username}
        secure_cookie = create_signed_value(
            cls.settings.COOKIE_SECRET, cookie_name,
            json_encode(cookie_value))
        return {'Cookie': '='.join((cookie_name, secure_cookie.decode()))}

    @property
    def auth_user(self):
        return self.cookie_header('goodguy@example.com')

    @property
    def evil_user(self):
        return self.cookie_header('villain@example.com')


class SmartAPITests(BaseTestCase):

    def test_000(self):
        assert isinstance('test', str)

    def test_001(self):
        assert API_Doc.exists(id='3912601003e25befedfb480a5687ab07')
    
    def test_002(self):
        assert not API_Doc.exists(id='somefakeid123456789')