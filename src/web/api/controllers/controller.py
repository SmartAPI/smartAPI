"""
Controller Classes for
- model.api_doc
Used by web.handlers
"""

import json
import logging

import elasticsearch
import requests
from elasticsearch import Elasticsearch, RequestError, helpers

from tornado.httpclient import HTTPResponse

from ..model.api_doc import API_Doc

from ..transform import (SWAGGER2_INDEXED_ITEMS, APIMetadata, decode_raw,
                        get_api_metadata_by_url, polite_requests)

logger = logging.getLogger(__name__)

ES_HOST = 'localhost:9200'
ES_INDEX_NAME = 'smartapi_oas3'

def get_es(es_host=None):
    es_host = es_host or ES_HOST
    es = Elasticsearch(es_host, timeout=120)
    return es

class APIDocController:

    def __init__(self, index=None, doc_type=None, es_host=None, _id=None):
        self._es = get_es(es_host)
        self._index = index or ES_INDEX_NAME
        # self._doc = API_Doc.get(id=_id)
        super().__init__() 

    @staticmethod
    def exists(schema):
        """
        schema: schema namespace
        """
        return API_Doc.exists(schema)

    # def __init__(self, _id):
    #     self._doc = API_Doc.get(id=_id)

    @property
    def user(self):
        return self._doc._meta.github_username

    @property
    def url(self):
        return self._doc._meta.url

    @property
    def slug(self):
        return self._doc._meta.slug

    @staticmethod
    def add(api_doc, save_v2=False, overwrite=False, user_name=None, override_owner=False, warn_on_identical=False, dryrun=False):
        metadata = APIMetadata(api_doc)
        doc = API_Doc(** metadata.convert_es())
        doc.save()      
        return doc

    @staticmethod
    def get_all(api_name=None):

        search = API_Doc.search()
        search.params(rest_total_hits_as_int=True)

        if user:
            search = search.query("term", ** {"info.title": api_name})
        else:
            search = search.query("match_all")

        return search
    
    def get_tags(self, field=None, size=100):
        """
            return a list of existing values for the given field.
        """
        use_raw=True
        _field = field + ".raw" if use_raw else field
        agg_name = 'field_values'
        doc = API_Doc()
        res = doc.aggregate(field= field, size= size, agg_name= agg_name)
        print(res.to_dict())
        return res.to_dict()
        

    def delete(self):

        self._doc.delete()

    def update(self, url, doc):
        # this overrides existing data
        # expect exception if no success
        logger.info("Update [%s] (%s)", self.slug, self.user)
        logger.debug(url)
        logger.debug(doc)

