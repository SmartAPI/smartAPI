# """
#     Biothings ESQueryHandler Type Tester
# """
# import os

# import pytest
# from biothings.tests.web import BiothingsTestCase

# from .setup import setup_es

# MYGENE_ID = "67932b75e2c51d1e1da2bf8263e59f0a"
# MYCHEM_ID = "8f08d1446e0bb9c2b323713ce83e2bd3"

# setup_es()
# @pytest.mark.skip("All tests failed by 404 response")
# class SmartAPIQueryTest(BiothingsTestCase):
#     def test_match_all(self):
#         res = self.query()
#         assert res["total"] == 2
#         res = self.query(q="__all__")
#         assert res["total"] == 2

#     def test_query_string(self):
#         res = self.query(q="mygene")
#         assert res["total"] == 1
#         res = self.query(q="mychem")
#         assert res["total"] == 1

#         # since we have a predefined scoring method,
#         # the order of this query is well defined
#         res = self.query(q="query mygene")
#         assert res["hits"][0]["_id"] == MYGENE_ID
#         assert res["hits"][1]["_id"] == MYCHEM_ID

#         res = self.query(q="tags.name:translator")
#         assert res["total"] == 2
#         res = self.query(q="tags.name:chemical")
#         assert res["total"] == 1
#         res = self.query(q="tags.name:gene")
#         assert res["total"] == 1

#     def test_query_filters(self):
#         res = self.query(authors='"Chunlei Wu"')
#         assert res["total"] == 2
#         res = self.query(authors="otheruser", hits=False)
#         assert res["total"] == 0
#         res = self.query(tags="translator")
#         assert res["total"] == 2
#         res = self.query(tags="chemical")
#         assert res["total"] == 1
#         res = self.query(tags="gene")
#         assert res["total"] == 1
#         res = self.query(authors='"Chunlei Wu"', tags="translator")
#         assert res["total"] == 2
#         res = self.query(authors='"Chunlei Wu"', tags="gene,chemical")
#         assert res["total"] == 2
#         res = self.query(authors="otheruser", tags="gene,chemical", hits=False)
#         assert res["total"] == 0
