"""
    Elasticsearch Document Object Base Model
"""
# pylint: disable=wildcard-import
# pylint: disable=unused-wildcard-import
from elasticsearch_dsl import A, Document, MetaField, connections

ES_HOST = "localhost:9200"

# create a default connection
connections.create_connection(hosts=ES_HOST)


class BaseDoc(Document):
    class Meta:
        """
        Index Mappings
        """

        dynamic = MetaField(True)
        abstract = True

    @classmethod
    def exists(cls, value, field="_id"):
        """
        Return the first matching document's _id or None.
        Data could change after query, use try-catch for
        any follow up operations like Document.get(_id).
        """
        search = cls.search().query("match", **{field: value})
        if search.count():
            return next(iter(search)).meta.id
        return None

    @classmethod
    def aggregate(cls, field="tags.name"):
        """
        Perform terms aggregation on a keyword field.
        Add multi-field keyword indexing suffix automatically.
        """

        if not field.endswith(".raw") and not field.startswith("_"):
            field = field + ".raw"  # so that it's a keyword field

        # build the aggregation query
        agg = A("terms", field=field, size=25)
        search = cls.search()
        search.aggs.bucket("aggs", agg)

        # transform the response to a simpler format
        buckets = search.execute().aggregations.aggs.buckets
        result = {b["key"]: b["doc_count"] for b in buckets}

        return result

    def get_url(self):
        raise NotImplementedError()
