from base64 import b64decode
from enum import Enum
from typing import OrderedDict, Dict

from biothings.web.query import AsyncESQueryBackend, AsyncESQueryPipeline, ESQueryBuilder, ESResultFormatter
from elasticsearch_dsl import Q, Search

from controller.base import OpenAPI, Swagger
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
        if options.get("raw") == 1:
            # do not trigger the RawResultInterrupt
            # supported by 'raw' parameter in query engine.
            # any value >1 still keeps that behavior.
            options["raw"] = None

        return await super().search(q, **options)

    async def fetch(self, id=None, **options):
        # id is None means listing all documents
        # with pagination parameters size and from.

        # Get Id
        if id is not None:
            # ignore match_all params.
            options.pop("size", None)
            options.pop("from", None)
            options["case"] = _CASE.GET_ID

            res = await super().fetch(id, **options)
            return OrderedDict(res)  # for YAML serialization

        # Match All
        # the score field is the same, and trivial for
        # a match_all query, exclude it in the result.
        options["score"] = False
        options["case"] = _CASE.GET_ALL
        res = await self.search(id, **options)
        return [OrderedDict(hit) for hit in res["hits"]]


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
            search = search.query("query_string", query=q)

        # term search
        elif q.startswith('"') and q.endswith('"'):
            query = {
                "query": {
                    "dis_max": {
                        "queries": [
                            {"term": {"_id": {"value": q.strip('"'), "boost": 5}}},
                            {"term": {"_meta.slug": {"value": q.strip('"'), "boost": 5}}},
                            {"match": {"info.title": {"query": q, "boost": 1.5, "operator": "AND"}}},
                            {
                                "query_string": {"query": q, "default_operator": "AND", "default_field": "all"}
                            },  # base score
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
                            {"query_string": {"query": q, "default_field": "all"}},  # base score
                            # ---------------------------------------------
                            {"wildcard": {"info.title": {"value": q + "*", "boost": 0.8}}},
                            {"wildcard": {"info.description": {"value": q + "*", "boost": 0.5}}},
                        ]
                    }
                }
            }
            search = search.update_from_dict(query)

        return search

    def apply_extras(self, search, options):
        """
        Process non-query options and customize their behaviors.
        Customized aggregation syntax string is translated here.
        """
        # apply extra filters from query parameters
        if options.authors:  # '"Chunlei Wu"'
            search = search.filter("terms", info__contact__name__raw=options.authors)

        if options.tags:  # '"chemical", "drug"'
            search = search.filter("terms", tags__name__raw=options.tags)

        # add aggregations
        facet_size = options.facet_size or 10
        for agg in options.aggs or []:
            term, bucket = agg, search.aggs
            while term:
                if self.allow_nested_query and "(" in term and term.endswith(")"):
                    _term, term = term[:-1].split("(", 1)
                else:
                    _term, term = term, ""
                bucket = bucket.bucket(_term, "terms", field=_term, size=facet_size)

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
        case = options.get("case", _CASE.QUERY)
        if case == _CASE.QUERY:  # decoding _raw is too slow for multi-hit queries.
            search = search.source(excludes=["_raw"], includes=options._source)
        else:  # decodes all fields from _raw by default. include other _fields.
            search = search.source(includes=options._source or ["_*"])
        # -------------------------------------------------------

        for key, value in options.items():
            if key in ("from", "size", "explain", "version"):
                search = search.extra(**{key: value})

        return search


class SmartAPIResultTransform(ESResultFormatter):
    def transform_hit(self, path, doc, options):
        if path == "":
            if "_raw" in doc:
                _raw = b64decode(doc.pop("_raw"))
                _raw = decoder.decompress(_raw)
                _raw = decoder.to_dict(_raw)
                doc.update(_raw)

            if options.raw == 0:
                for key in list(doc.keys()):
                    if key.startswith("_"):
                        doc.pop(key)

            if isinstance(doc.get("paths"), list):
                doc["paths"] = {item["path"]: item.get("pathitem", {}) for item in doc["paths"]}

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
                if "openapi" in doc:
                    _doc = OpenAPI(doc)
                    _doc.order()
                    # meta fields appear first
                    for key in list(doc.keys()):
                        if not key.startswith("_"):
                            doc.pop(key)
                    doc.update(_doc)

                elif "swagger" in doc:
                    _doc = Swagger(doc)
                    _doc.order()
                    # meta fields appear first
                    for key in list(doc.keys()):
                        if not key.startswith("_"):
                            doc.pop(key)
                    doc.update(_doc)


class MetaKGQueryBuilder(ESQueryBuilder):
    def apply_extras(self, search, options):
        """
        apply extra filters
        """
        if not options._source:
            # by default exclude api.bte or bte field, but can be included by specifying in the fields parameter
            options._source = ["-api.bte", "-bte"]

        search = super().apply_extras(search, options)
        # apply extra filters from query parameters
        if options.subject:
            search = search.filter("terms", subject=options.subject)

        if options.object:
            search = search.filter("terms", object=options.object)

        if options.predicate:
            search = search.filter("terms", predicate=options.predicate)
        if options.node:
            # either subject or object
            search = search.filter(Q("terms", subject=options.node) | Q("terms", object=options.node))

        return search

class MetaKGESQueryBackend(AsyncESQueryBackend):
    """
    Extends AsyncESQueryBackend to dynamically select ElasticSearch indices for MetaKG based 
    on query option, consolidated.

    Methods:
        adjust_index(original_index: str, query: str, **options: Dict) -> str:
            Adjusts the ElasticSearch index based on the 'consolidated' option in the query.
            - original_index: The default index.
            - query: The search query string.
            - options: Dictionary of query options, where 'consolidated' determines the index choice.
    """

    def adjust_index(self, original_index: str, query: str, **options: Dict) -> str:
        query_index = original_index
        consolidated = options.get("consolidated", True)
        
        if consolidated:
            query_index = self.indices.get("metakg_consolidated", None)
        else:
            query_index = self.indices.get("metakg", None)
        return query_index

class MetaKGQueryPipeline(AsyncESQueryPipeline):
    def __init__(self, *args, **kwargs):
        # ns is an instance of BiothingsNamespace
        ns = kwargs.pop("ns", None)
        if ns:
            if not kwargs.get("builder"):
                kwargs["builder"] = MetaKGQueryBuilder()
            if not kwargs.get("backend"):
                kwargs["backend"] = MetaKGESQueryBackend(
                    ns.elasticsearch.async_client,
                    ns.config.ES_INDICES,
                    ns.config.ES_SCROLL_TIME,
                    ns.config.ES_SCROLL_SIZE,
                )
            if not kwargs.get("formatter"):
                kwargs["formatter"] = ESResultFormatter(
                    ns.elasticsearch.metadata.biothing_licenses,
                    ns.config.LICENSE_TRANSFORM,
                    ns.fieldnote.get_field_notes(),
                    ns.config.AVAILABLE_FIELDS_EXCLUDED,
                )
        super().__init__(*args, **kwargs)
