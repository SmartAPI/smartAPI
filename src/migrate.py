import base64

from elasticsearch.client import Elasticsearch
from elasticsearch.helpers import scan

from controller import ConflictError, ControllerError, OpenAPI, SmartAPI, Swagger
from model import APIDoc
from utils import decoder

ES_DESTINATION = "http://18.237.41.215:9200"


class MigrationSmartAPI(SmartAPI):

    def validate(self):

        if not self.version:
            raise ControllerError("Unknown version.")

        if self.version == 'openapi':
            doc = OpenAPI(self._data)
        else:  # then it must be swagger
            doc = Swagger(self._data)

        # NOTE OVERRIDE
        # try:
        #     doc.validate()  # basing on its format
        # except ValueError as err:
        #     raise ControllerError(str(err)) from err

        return doc

    def save(self, timestamp, **kwargs):

        if not self.username:
            raise ControllerError("Username is required.")

        if self.url is self.VALIDATION_ONLY:
            raise ControllerError("In validation-only mode.")

        _doc = self.validate()
        _doc.clean()  # only keep indexing fields

        # NOTE
        # OVERRIDE
        # if self.slug:
        #     _id = self.find(self.slug)
        #     if _id and _id != self._id:  # another doc same slug.
        #         raise ConflictError("Slug is already registered.")

        # NOTE
        # if the slug of another document changed at this point
        # it's possible to have two documents with the same slug
        # registered. but it should be rare enough in reality.

        doc = APIDoc(**_doc)
        doc.meta.id = self._id
        doc._meta.url = self.url
        doc._meta.timestamp = timestamp  # TODO HERE IS AN OVERRIDE
        doc._meta.username = self.username
        doc._meta.slug = self.slug
        doc._raw = decoder.compress(self.raw)
        doc.save(**kwargs)  # TODO HERE IS AN OVERRIDE

        return self._id


def main():

    client = Elasticsearch(ES_DESTINATION)

    for doc in scan(
        Elasticsearch("http://smart-api.info:9200"),
        query={"query": {"match_all": {}}},
        index="smartapi_oas3",
        doc_type="api"
    ):
        print(doc["_id"])
        if not doc['_source']['_meta'].get('_archived'):
            url = doc['_source']['_meta']['url']
            raw = decoder.decompress(base64.urlsafe_b64decode(doc['_source']['~raw']))

            smartapi = MigrationSmartAPI(url, raw)
            smartapi.username = doc['_source']['_meta']['github_username']
            smartapi.slug = doc['_source']['_meta'].get('slug')
            smartapi.save(doc['_source']['_meta']['timestamp'], using=client)


if __name__ == "__main__":
    main()
