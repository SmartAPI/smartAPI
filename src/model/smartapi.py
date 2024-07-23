"""
    Elasticsearch Document Object Model for SmartAPI
"""

from config import ES_INDICES
from elasticsearch_dsl import Binary, Boolean, Date, InnerDoc, Integer, Keyword, Object, Text, mapping

from .base import BaseDoc

smartapi_mapping = {
    "dynamic_templates": [
        {
            "ignore_example_field": {
                "path_match": "*.example",
                "mapping": {"index": False, "type": "text"},
            }
        },
        {"ignore_examples_field": {"match": "examples", "mapping": {"enabled": False}}},
        {"ignore_ref_field": {"match": "$ref", "match_pattern": "simple", "mapping": {"index": False}}},
        {"ignore_schema_field": {"match": "schema", "mapping": {"enabled": False}}},
        {"ignore_content_field": {"match": "content", "mapping": {"enabled": False}}},
        {
            "ignore_default_field": {
                "match": "default",
                "mapping": {"type": "object", "enabled": False},
            }
        },
        {
            "template_1": {
                "match": "*",
                "match_mapping_type": "string",
                "mapping": {
                    "type": "text",
                    "fields": {"raw": {"type": "keyword", "ignore_above": 512}},
                    "copy_to": "all",
                },
            }
        },
    ],
    "properties": {
        "components": {"enabled": False},
        "definitions": {"enabled": False},
        "_raw": {"type": "binary"},
        "all": {"type": "text"},
    },
}


_smartapi_mapping = mapping.Mapping()
_smartapi_mapping.meta("dynamic_templates", smartapi_mapping["dynamic_templates"])
# disable two fields with dynamic data structure
_smartapi_mapping.field("components", "object", enabled=False)
_smartapi_mapping.field("definitions", "object", enabled=False)
_smartapi_mapping.field("all", "text")  # the default all field for unfielded queries


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
    has_metakg = Boolean()


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

    class Meta:
        mapping = _smartapi_mapping

    class Index:
        """
        Index Settings
        """

        name = ES_INDICES["metadata"]
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0,
            "index.mapping.ignore_malformed": True,
            "index.mapping.total_fields.limit": 2500,
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
