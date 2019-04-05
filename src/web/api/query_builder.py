from biothings.web.api.es.query_builder import ESQueryBuilder as BiothingsESQueryBuilder

import json


class SmartAPIQueryBuilder(BiothingsESQueryBuilder):

    def get_query_filters(self):

        _filter = None

        if self.options.filters:
            try:
                terms_filter = json.loads(self.options.filters)
                if terms_filter:
                    if len(terms_filter) == 1:
                        _filter = {"terms": terms_filter}
                    else:
                        _filter = [{"terms": {f[0]: f[1]}}
                                   for f in terms_filter.items()]
            except:
                pass

        return _filter

    def get_missing_filters(self):

        no_archived = {
            "term": {
                "_meta._archived": "true"
            }
        }
        return no_archived

    def _extra_query_types(self, q):

        dis_max_query = {
            "query": {
                "dis_max": {
                    "queries": [
                        {
                            "term": {
                                "info.title": {
                                    "value": q,
                                    "boost": 2.0
                                }
                            }
                        },
                        {
                            "term": {
                                "server.url": {
                                    "value": q,
                                    "boost": 1.1
                                }
                            }
                        },
                        {
                            "term": {
                                "_id": q,
                            }
                        },
                        {
                            "query_string": {
                                "query": q
                            }
                        },
                        {
                            "query_string": {
                                "query": q + "*",
                                "boost": 0.8
                            }
                        },
                    ]
                }
            }
        }
        return dis_max_query

    def _query_GET_query(self, q):
        # override as an alternative solution
        # see change below
        if self._is_user_query():
            _query = self._user_query(q)
        elif self._is_match_all(q):
            _query = self._match_all(q)
        elif self._is_random_query(q) and self.allow_random_query:
            _query = self._random_query(q)
        else:
            _query = self._extra_query_types(q)

        if not _query:
            _query = self._default_query(q)

        # previously assigned to _query directly
        _query['query'] = self.add_query_filters(_query)

        _query = self.queries.raw_query(_query)

        _ret = self._return_query_kwargs({'body': _query})

        if self.options.fetch_all:
            _ret['body'].pop('sort', None)
            _ret['body'].pop('size', None)
            _ret.update(self.scroll_options)
        return _ret
