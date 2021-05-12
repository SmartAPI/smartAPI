
from base64 import b64decode

from biothings.utils.web.es_dsl import AsyncSearch
from biothings.web.pipeline import ESQueryBuilder, ESResultTransform

from controller import OpenAPI, Swagger
from utils import decoder


class SmartAPIQueryBuilder(ESQueryBuilder):

    def default_string_query(self, q, options):

        search = AsyncSearch()

        if q == '__all__':
            search = search.query()

        elif q == '__any__' and self.allow_random_query:
            search = search.query('function_score', random_score={})

        # elasticsearch query string syntax
        elif ":" in q or " AND " in q or " OR " in q:
            search = search.query('query_string', query=q)

        else:  # simple text search
            query = {
                "query": {
                    "dis_max": {
                        "queries": [
                            {"term": {"_id": {"value": q, "boost": 5}}},
                            {"term": {"_meta.slug": {"value": q, "boost": 3}}},
                            {"match": {"info.title": {"query": q, "boost": 1.5}}},
                            {"term": {"servers.url": {"value": q, "boost": 1.1}}},
                            # ---------------------------------------------
                            {"query_string": {"query": q}},  # base score
                            # ---------------------------------------------
                            {"wildcard": {"info.title": {"value": q + "*", "boost": 0.8}}},
                            {"wildcard": {"info.description": {"value": q + "*", "boost": 0.5}}},
                        ]
                    }
                }
            }
            search = AsyncSearch()
            search = search.update_from_dict(query)

        search = search.params(rest_total_hits_as_int=True)
        search = search.source(exclude=['_raw'], include=options._source)

        if options.authors:  # '"Chunlei Wu"'
            search = search.filter('terms', info__contact__name__raw=options.authors)

        if options.tags:  # '"chemical", "drug"'
            search = search.filter('terms', tags__name__raw=options.tags)

        return search

    def default_match_query(self, q, scopes, options):
        search = super().default_match_query(q, scopes, options)
        search = search.source(include=options._source or ['_*'])
        return search

    def _apply_extras(self, search, options):
        """
        Process non-query options and customize their behaviors.
        Customized aggregation syntax string is translated here.
        """

        # add aggregations
        facet_size = options.facet_size or 10
        for agg in options.aggs or []:
            term, bucket = agg, search.aggs
            while term:
                if self.allow_nested_query and \
                        '(' in term and term.endswith(')'):
                    _term, term = term[:-1].split('(', 1)
                else:
                    _term, term = term, ''
                bucket = bucket.bucket(
                    _term, 'terms', field=_term, size=facet_size)

        # add es params
        if isinstance(options.sort, list):
            # accept '-' prefixed field names
            search = search.sort(*options.sort)

        # OVERRIDE
        # -------------------------------------------------------
        # if isinstance(options._source, list):
        #     if 'all' not in options._source:
        #         search = search.source(options._source)
        # -------------------------------------------------------

        for key, value in options.items():
            if key in ('from', 'size', 'explain', 'version'):
                search = search.extra(**{key: value})

        return search


class SmartAPIResultTransform(ESResultTransform):

    def transform_hit(self, path, doc, options):

        if path == '':
            doc.pop('_index')
            doc.pop('_type', None)    # not available by default on es7
            doc.pop('sort', None)     # added when using sort
            doc.pop('_node', None)    # added when using explain
            doc.pop('_shard', None)   # added when using explain

            # OVERRIDE STARTS HERE

            if "_raw" in doc:
                _raw = b64decode(doc.pop('_raw'))
                _raw = decoder.decompress(_raw)
                _raw = decoder.to_dict(_raw)
                doc.update(_raw)

            if options.raw == 0:
                for key in list(doc.keys()):
                    if key.startswith('_'):
                        doc.pop(key)

            if isinstance(doc.get('paths'), list):
                doc['paths'] = {
                    item['path']: item.get('pathitem', {})
                    for item in doc['paths']
                }

            # NOTE
            # Root field filtering in transform stage (if necessary)
            # ---------------------------------------------------------------
            # if options._source:
            #     fields = {field.split('.')[0] for field in options._source}
            #     for key in list(doc.keys()):
            #         if key not in fields:
            #             doc.pop(key)

            # field ordering
            if not options.sorted:

                if 'openapi' in doc:
                    _doc = OpenAPI(doc)
                    _doc.order()
                    # meta fields appear first
                    for key in list(doc.keys()):
                        if not key.startswith('_'):
                            doc.pop(key)
                    doc.update(_doc)

                elif 'swagger' in doc:
                    _doc = Swagger(doc)
                    _doc.order()
                    # meta fields appear first
                    for key in list(doc.keys()):
                        if not key.startswith('_'):
                            doc.pop(key)
                    doc.update(_doc)
