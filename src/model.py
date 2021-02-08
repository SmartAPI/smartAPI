"""
    Elasticsearch Document Object Model
"""
import os

# pylint: disable=wildcard-import
# pylint: disable=unused-wildcard-import
from elasticsearch_dsl import *


# parse environment variables
ES_HOST = os.getenv('ES_HOST', 'localhost:9200')
ES_INDEX_NAME = 'smartapi_docs'

# create a default connection
connections.create_connection(hosts=ES_HOST)


class UserMeta(InnerDoc):
    """ The _meta field. """
    username = Keyword(required=True)
    timestamp = Date(default_timezone='UTC')
    url = Keyword(required=True)
    slug = Keyword()


class StatMeta(InnerDoc):
    """ The _status field. """
    uptime_status = Keyword()
    uptime_ts = Date()

    refresh_status = Integer()
    refresh_ts = Date()


class APIDoc(Document):

    _meta = Object(UserMeta, required=True)
    _status = Object(StatMeta)
    _raw = Binary()

    info = Object()
    paths = Nested(
        multi=True,
        properties={
            "path": Text(),
            "pathitem": Nested(multi=True)
        })
    tags = Object(multi=True)
    openapi = Text()

    # swagger only fields
    swagger = Text()
    basePath = Text()
    host = Text()

    class Meta:
        """
        Index Mappings
        """
        dynamic = MetaField(True)

    class Index:
        """
        Index Settings
        """
        name = ES_INDEX_NAME
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0
        }

    @ classmethod
    def exists(cls, value, field="_id"):
        """
        Return the first matching document's _id or None.
        Data could change after query, use try-catch for
        any follow up operations like Document.get(_id).
        """
        search = cls.search().query('match', **{field: value})
        if search.count():
            return next(iter(search)).meta.id
        return None

    @ classmethod
    def aggregate(cls, field="tags.name"):
        """
        Perform terms aggregation on a keyword field.
        Add multi-field keyword indexing suffix automatically.
        """

        if not field.endswith(".raw") and not field.startswith("_"):
            field = field + ".raw"  # so that it's a keyword field

        # build the aggregation query
        agg = A('terms', field=field, size=25)
        search = cls.search()
        search.aggs.bucket("aggs", agg)

        # transform the response to a simpler format
        buckets = search.execute().aggregations.aggs.buckets
        result = {b['key']: b['doc_count'] for b in buckets}

        return result
