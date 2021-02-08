import base64

from elasticsearch.client import Elasticsearch
from elasticsearch.helpers import scan

from controller import SmartAPI
from utils import decoder, indices

ES_ORIGIN = "http://smart-api.info:9200"
ES_DESTINATION = "http://localhost:9200"  # CANNOT CHANGE THIS


def migrate():

    for doc in scan(
        Elasticsearch(ES_ORIGIN),
        query={"query": {"match_all": {}}},
        index="smartapi_oas3",
        doc_type="api"
    ):
        print(doc["_id"])
        if not doc['_source']['_meta'].get('_archived'):
            url = doc['_source']['_meta']['url']
            raw = decoder.decompress(base64.urlsafe_b64decode(doc['_source']['~raw']))

            smartapi = SmartAPI(url, doc['_source']['_meta']['timestamp'])
            smartapi.raw = raw
            smartapi.username = doc['_source']['_meta']['github_username']
            smartapi.slug = doc['_source']['_meta'].get('slug')
            smartapi.save(update_ts=False)
    print()


def update():

    for doc in scan(
        Elasticsearch(ES_DESTINATION),
        query={"query": {"match_all": {}}},
        index="smartapi_docs",
        scroll="60m"
    ):
        print(doc["_id"])
        smartapi = SmartAPI.get(doc["_id"])
        print(smartapi.check())
        print(smartapi.refresh())
        if smartapi.webdoc.status == 299:
            smartapi.webdoc._status = 200  # change status not reliable during migration
        smartapi.save(update_ts=False)
    print()


if __name__ == "__main__":
    input('Will reset smartapi_docs index. Ctrl-C to cancel.')
    indices.reset()
    migrate()
    indices.refresh()
    update()
