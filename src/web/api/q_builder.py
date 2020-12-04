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

    def _extra_query_options(self, search, options):

        search = AsyncSearch().query(
            "function_score",
            query=search.query,
            score_mode="first")

        if options.filters:
            if 'all' not in options.filters:
                search = search.filter('terms', _meta__slug=options.filters)

        return search