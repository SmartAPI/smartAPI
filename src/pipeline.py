
from biothings.utils.web.es_dsl import AsyncSearch
from biothings.web.pipeline import ESQueryBuilder, ESResultTransform


class SmartAPIQueryBuilder(ESQueryBuilder):

    def default_string_query(self, q, options):

        search = AsyncSearch()

        if q == '__all__':
            search = search.query()

        elif q == '__any__' and self.allow_random_query:
            search = search.query('function_score', random_score={})

        else:  # override
            query = {
                "query": {
                    "dis_max": {
                        "queries": [
                            {"term": {"info.title": {"value": q, "boost": 2.0}}},
                            {"term": {"server.url": {"value": q, "boost": 1.1}}},
                            {"term": {"_id": q}},
                            {"wildcard": {"info.title": {"value": q + "*"}}},
                            {"wildcard": {"info.description": {"value": q + "*"}}},
                            {"query_string": {"query": q}},
                        ]
                    }
                }
            }
            search = AsyncSearch()
            search = search.update_from_dict(query)

        search = search.params(rest_total_hits_as_int=True)
        search = search.source(exclude=['_raw'])

        if options.authors:  # '"Chunlei Wu"'
            search = search.filter('terms', info__contact__name__raw=options.authors)

        if options.tags:  # '"chemical", "drug"'
            search = search.filter('terms', tags__name__raw=options.tags)

        return search


class SmartAPIResultTransform(ESResultTransform):

    def transform_hit(self, path, doc, options):

        if path == '':
            doc.pop('_index')
            doc.pop('_type', None)    # not available by default on es7
            doc.pop('sort', None)     # added when using sort
            doc.pop('_node', None)    # added when using explain
            doc.pop('_shard', None)   # added when using explain

            # OVERRIDE
            # TODO TEST CASES
            try:
                doc['paths'] = {
                    item['path']: item['pathitem']
                    for item in doc['paths']
                }
            except Exception:
                pass
