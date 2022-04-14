
from base64 import b64decode
from enum import Enum
from typing import OrderedDict

from biothings.web.query import (
    AsyncESQueryPipeline,
    ESQueryBuilder,
    ESResultFormatter)
from elasticsearch_dsl import Search

from controller import OpenAPI, Swagger
from utils import decoder


# There are three types of cases supported:
# 1. match_all query for /api/metadata
# 2. match query for /api/metadata/_id
# 3. query string query for /api/metadata/query
class _CASE(Enum):
    GET_ALL = 1
    GET_ID = 2
    QUERY = 3


class SmartAPIQueryPipeline(AsyncESQueryPipeline):

    # in addition to document retrival,
    # the smartapi fetch endpoint also supports
    # listing all documents through pagination.
    # (match_all)

    async def search(self, q, **options):

        # raw == 1 means keeping _meta field
        # as oppposed to the default value 0
        if options.get('raw') == 1:
            # do not trigger the RawResultInterrupt
            # supported by 'raw' parameter in query engine.
            # any value >1 still keeps that behavior.
            options['raw'] = None

        return await super().search(q, **options)

    async def fetch(self, id=None, **options):

        # id is None means listing all documents
        # with pagination parameters size and from.

        # Get Id
        if id is not None:
            # ignore match_all params.
            options.pop('size', None)
            options.pop('from', None)
            options['case'] = _CASE.GET_ID

            res = await super().fetch(id, **options)
            return OrderedDict(res)  # for YAML serialization

        # Match All
        # the score field is the same, and trivial for
        # a match_all query, exclude it in the result.
        options['score'] = False
        options['case'] = _CASE.GET_ALL
        res = await self.search(id, **options)
        return [OrderedDict(hit) for hit in res['hits']]


class SmartAPIQueryBuilder(ESQueryBuilder):

    # About _raw field translation:
    # In use cases 1 and 2, it is expected to present
    # live-decoded original documents from _raw field
    # unless the user specifies _source to return.

    def default_string_query(self, q, options):

        search = Search()
        q = q.strip()

        # elasticsearch query string syntax
        if ":" in q or " AND " in q or " OR " in q:
            search = search.query('query_string', query=q)

        # term search
        elif q.startswith('"') and q.endswith('"'):
            query = {
                "query": {
                    "dis_max": {
                        "queries": [
                            {"term": {"_id": {"value": q.strip('"'), "boost": 5}}},
                            {"term": {"_meta.slug": {"value": q.strip('"'), "boost": 5}}},
                            {"match": {"info.title": {"query": q, "boost": 1.5, "operator": "AND"}}},
                            {"query_string": {"query": q, "default_operator": "AND"}}  # base score
                        ]
                    }
                }
            }
            search = search.update_from_dict(query)

        else:  # simple text search
            query = {
                "query": {
                    "dis_max": {
                        "queries": [
                            {"term": {"_id": {"value": q, "boost": 5}}},
                            {"term": {"_meta.slug": {"value": q, "boost": 5}}},
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
            search = search.update_from_dict(query)

        if options.authors:  # '"Chunlei Wu"'
            search = search.filter('terms', info__contact__name__raw=options.authors)

        if options.tags:  # '"chemical", "drug"'
            search = search.filter('terms', tags__name__raw=options.tags)

        return search

    def apply_extras(self, search, options):
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
        case = options.get('case', _CASE.QUERY)
        if case == _CASE.QUERY:  # decoding _raw is too slow for multi-hit queries.
            search = search.source(exclude=['_raw'], include=options._source)
        else:  # decodes all fields from _raw by default. include other _fields.
            search = search.source(include=options._source or ['_*'])
        # -------------------------------------------------------

        for key, value in options.items():
            if key in ('from', 'size', 'explain', 'version'):
                search = search.extra(**{key: value})

        return search


class SmartAPIResultTransform(ESResultFormatter):

    def transform_hit(self, path, doc, options):

        if path == '':

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
