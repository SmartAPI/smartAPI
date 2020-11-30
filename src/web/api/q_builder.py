from biothings.utils.web.es_dsl import AsyncSearch
from biothings.web.pipeline import ESQueryBuilder


class SmartAPIQueryBuilder(ESQueryBuilder):

    def default_string_query(self, q, options):

        query = {
            "query": {
                "dis_max": {
                    "queries": [
                        {"term": {"info.title": {"value": q, "boost": 2.0}}},
                        {"term": {"server.url": {"value": q, "boost": 1.1}}},
                        {"term": {"_id": q}},
                        {"query_string": {"query": q}},
                        {"query_string": {"query": q + "*", "boost": 0.8}}
                    ]
                }
            }
        }

        search = AsyncSearch()
        search = search.update_from_dict(query)
        search = search.params(rest_total_hits_as_int=True)
        return search