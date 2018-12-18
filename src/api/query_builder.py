from biothings.web.api.es.query_builder import ESQueryBuilder as BiothingsESQueryBuilder

import json

class SmartAPIQueryBuilder(BiothingsESQueryBuilder):

    def get_query_filters(self):

        _filter = None

        if self.options.filters:
            try:
                terms_filter = json.loads(self.options.filters)
                if terms_filter:
                    _filter =  { "terms": terms_filter }
            except:
                pass

        return _filter

    def get_missing_filters(self):

        no_archived = {
            "term": {
               "_meta._archived":"true"
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