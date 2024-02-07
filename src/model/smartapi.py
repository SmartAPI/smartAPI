"""
    Elasticsearch Document Object Model for SmartAPI
"""
from elasticsearch_dsl import Binary, Date, InnerDoc, Integer, Keyword, Object, Text, Boolean

from config import SMARTAPI_ES_INDEX

from .base import BaseDoc


class StatMeta(InnerDoc):
    """The _status field."""

    uptime_status = Keyword()
    uptime_msg = Text(index=False)
    uptime_ts = Date()

    refresh_status = Integer()
    refresh_ts = Date()


class UserMeta(InnerDoc):
    """The _meta field."""

    url = Keyword(required=True)
    slug = Keyword()  # url shortcut
    username = Keyword(required=True)
    date_created = Date(default_timezone="UTC")
    last_updated = Date(default_timezone="UTC")
    has_metakg = Boolean(default=False)


class SmartAPIDoc(BaseDoc):
    _status = Object(StatMeta)
    _raw = Binary()
    _meta = Object(UserMeta, required=True)

    info = Object()
    servers = Object()
    paths = Object(properties={"path": Text(), "pathitem": Object()})
    tags = Object(multi=True)
    openapi = Text()

    # swagger only fields
    swagger = Text()
    basePath = Text()
    host = Text()

    class Index:
        """
        Index Settings
        """

        name = SMARTAPI_ES_INDEX
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0,
            "mapping.ignore_malformed": True,
            "mapping.total_fields.limit": 2500,
        }

    def get_url(self):
        return self._meta.url

    @classmethod
    def get_default_server_url(cls, servers):
        """Get the default server from the servers list."""
        # return the first server with production maturity
        for server in servers:
            if server.get("x-maturity", None) == "production":
                return server.get("url")
        # then check for description for word "production"
        for server in servers:
            if server.get("description", "").lower().find("production") != -1:
                return server.get("url")
        # then use https URL first
        for server in servers:
            if server.get("url", "").startswith("https"):
                return server.get("url")
        # finally, just return the first available one
        return servers[0].get("url")
