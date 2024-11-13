"""
    Biothings ESQueryHandler Type Tester
"""
import pytest
from biothings.tests.web import BiothingsWebAppTest
from controller import SmartAPI
from utils.indices import delete, refresh, reset

ES_INDEX_NAME = "smartapi_docs_test"

MYGENE_URL = (
    "https://raw.githubusercontent.com/NCATS-Tangerine/translator-api-registry/master/mygene.info/openapi_minimum.yml"
)
MYCHEM_URL = (
    "https://raw.githubusercontent.com/NCATS-Tangerine/translator-api-registry/master/mychem.info/openapi_full.yml"
)

MYGENE_ID = "67932b75e2c51d1e1da2bf8263e59f0a"
MYCHEM_ID = "8f08d1446e0bb9c2b323713ce83e2bd3"


@pytest.fixture(scope="module", autouse=True)
def setup():
    """
    setup state called once for the class
    """
    SmartAPI.INDEX = ES_INDEX_NAME
    reset(SmartAPI.MODEL_CLASS, index=ES_INDEX_NAME)

    mygene = SmartAPI(MYGENE_URL)
    mygene.raw = b"{\"test\": null}"
    mygene.username = "tester"
    mygene.refresh()
    mygene.check()
    mygene.save()

    mychem = SmartAPI(MYCHEM_URL)
    mychem.raw = b"{\"test\": null}"
    mychem.username = "tester"
    mychem.refresh()
    mychem.check()
    mychem.save()

    refresh(index=ES_INDEX_NAME)


# @pytest.mark.skip("All tests failed by 404 response")
class SmartAPIQueryTest(BiothingsWebAppTest):
    prefix = ""

    def query(self, method="GET", endpoint="/api/query", **kwargs):
        return super().query(method=method, endpoint=endpoint, **kwargs)

    def test_match_all(self):
        res = self.query()
        assert res["total"] == 2
        res = self.query(q="__all__")
        assert res["total"] == 2

    def test_query_string(self):
        res = self.query(q="mygene")
        assert res["total"] == 1
        res = self.query(q="mychem")
        assert res["total"] == 1

        # since we have a predefined scoring method,
        # the order of this query is well defined
        res = self.query(q="query gene", meta=1, fields="_meta")
        assert res["hits"][0]["_id"] == MYGENE_ID
        assert res["hits"][1]["_id"] == MYCHEM_ID

        res = self.query(q="tags.name:translator")
        assert res["total"] == 2
        res = self.query(q="tags.name:chemical")
        assert res["total"] == 1
        res = self.query(q="tags.name:gene")
        assert res["total"] == 1

    def test_query_filters(self):
        res = self.query(authors='"Chunlei Wu"')
        assert res["total"] == 2
        res = self.query(authors="otheruser", hits=False)
        assert res["total"] == 0
        res = self.query(tags="translator")
        assert res["total"] == 2
        res = self.query(tags="chemical")
        assert res["total"] == 1
        res = self.query(tags="gene")
        assert res["total"] == 1
        res = self.query(authors='"Chunlei Wu"', tags="translator")
        assert res["total"] == 2
        res = self.query(authors='"Chunlei Wu"', tags="gene,chemical")
        assert res["total"] == 2
        res = self.query(authors="otheruser", tags="gene,chemical", hits=False)
        assert res["total"] == 0


def teardown_module():
    delete(SmartAPI.MODEL_CLASS, index=SmartAPI.INDEX)
    SmartAPI.INDEX = None
