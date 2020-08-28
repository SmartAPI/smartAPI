"""
Controller Classes for
- model.api_doc
Used by web.handlers
"""

import json
import logging
import string

import elasticsearch
import requests
from elasticsearch import Elasticsearch, RequestError, helpers
from elasticsearch_dsl import *

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
        doc = API_Doc()
        self._doc = doc.get(id=_id)

    @staticmethod
    def exists(_id):
        """
        schema: schema namespace
        """
        doc = API_Doc()
        return doc.exists(_id=_id)

    @property
    def user(self):
        return self._doc._meta.github_username

    @property
    def url(self):
        return self._doc._meta.url

    @property
    def slug(self):
        return self._doc._meta.slug

    def add(api_doc, save_v2=False, overwrite=False, user_name=None, override_owner=False, warn_on_identical=False, dryrun=False):
        metadata = APIMetadata(api_doc)

        # validate document schema
        valid = metadata.validate(raise_error_on_v2=not save_v2)
        if not valid['valid']:
            valid['success'] = False
            valid['error'] = '[Validation] ' + valid['error']
            return valid

        # avoid unintended overwrite
        # generates an id based on source url
        api_id = metadata.encode_api_id()
        doc_exists = APIDocController.exists(api_id)
        print(f"\033[93m"+"API EXISTS: "+"\033[0m", doc_exists)
        print(f"\033[93m"+"OVERWRITE: "+"\033[0m", overwrite)
        print(f"\033[93m"+"OVERWRITE OWNER: "+"\033[0m", override_owner)
        if doc_exists:
            if not overwrite:
                print(f"\033[93m"+"NOT!!! OVERWRITE: "+"\033[0m", overwrite)
                return {"success": False, "error": "[Conflict] API exists. Not saved."}
            elif not override_owner:
                # Check user is owner
                i = API_Doc.get(id=api_id).to_dict()
                _owner = i.get('_meta', {}).get('github_username', '')               
                if _owner != user_name:
                    return {"success": False, "error": "[Conflict] User mismatch. Not Saved."}
                print(f"\033[93m"+"API EXISTS AND OWNER IS: "+"\033[0m", _owner)     

        # save to es index
        if dryrun:
            print(f"\033[93m"+"IS DRYRUN: "+"\033[0m", dryrun)
            return {"success": True, '_id': "[Dryrun] this is a dryrun. API is not saved.", "dryrun": True}

        print(f"\033[93m"+"SAVE NEW: "+"\033[0m")
        # save doc with generated id
        doc = API_Doc(meta={'id':api_id}, ** metadata.convert_es())
        doc.save()      
        return {"success": True, "dryrun": False}

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
        

    def delete(self, _id, user):
        '''
            delete api from index
            UPDATED TO DSL
        '''
        i = API_Doc.get(id=_id).to_dict()
        _user = i.get('_meta', {}).get('github_username', '')

        # Make sure this is the correct user
        if user.get('login', None) != _user:
            return (405, {"success": False, "error": "User '{}' is not the owner of API '{}'".format(user.get('login', None), _id)})

        self._doc.delete(id=_id)
        Index(API_Doc.Index.name).refresh()
        return (200, {"success": True})

    def update(self, _id, user, slug_name):
        ''' 
            set the slug name of API _id to slug_name. 
             UPDATED TO DSL
        '''
        if not self.exists(_id):
            return (404, {"success": False, "error": "Could not retrieve API '{}' to set slug name".format(_id)})

        i = API_Doc.get(id=_id).to_dict()
        _user = i.get('_meta', {}).get('github_username', '')

        # Make sure this is the correct user
        if user.get('login', None) != _user:
            return (405, {"success": False, "error": "User '{}' is not the owner of API '{}'".format(user.get('login', None), _id)})

        print(f"\033[93m"+" User matches: "+"\033[0m", _user)
        # validate the slug name
        _valid, _resp = self._validate_slug_name(slug_name=slug_name)

        if not _valid:
            return (405, _resp)

        # doc = API_Doc()
        # doc = doc.get(id=_id)
        self._doc.update(id=_id, refresh=True, _meta={"slug":slug_name.lower()} )

        return (200, {"success": True, "{}._meta.slug".format(_id): slug_name.lower()})


    def _validate_slug_name(self, slug_name):
        ''' 
            Function that determines whether slug_name is a valid slug name 
            UPDATED TO DSL
        '''
        _valid_chars = string.ascii_letters + string.digits + "-_~"
        _slug = slug_name.lower()

        # reserved for dev node, normal web functioning
        if _slug in ['www', 'dev', 'smart-api']:
            return (False, {"success": False, "error": "Slug name '{}' is reserved, please choose another".format(_slug)})

        # length requirements
        if len(_slug) < 4 or len(_slug) > 50:
            return (False, {"success": False, "error": "Slug name must be between 4 and 50 chars"})

        # character requirements
        if not all([x in _valid_chars for x in _slug]):
            return (False, {"success": False, "error": "Slug name contains invalid characters.  Valid characters: '{}'".format(_valid_chars)})

        # does it exist already?
        doc = API_Doc()
        if doc.slug_exists(slug=_slug):
            return (False, {"success": False, "error": "Slug name '{}' already exists, please choose another".format(_slug)})

        # good name
        return (True, {})
    
    # def refresh_api(self, api_doc, user=None, override_owner=False, dryrun=True,
    #                  error_on_identical=False, save_v2=False):
    def refresh_api(self, _id, user):
        ''' refresh the given API document object based on its saved metadata url  '''

        doc = API_Doc(id=_id)
        api_doc = doc.get(id=_id).to_dict()
        print(f"\033[93m"+"DOC TO UPDATE "+"\033[0m", api_doc)

        _meta = api_doc.get('_meta', {})

        res = get_api_metadata_by_url(_meta['url'])
        
        if res and isinstance(res, dict):
            if res.get('success', None) is False:
                res['error'] = '[Request] '+res.get('error', '')
                status = res
            else:
                _meta['timestamp'] = datetime.now().isoformat()
                res['_meta'] = _meta
                print(f"\033[93m"+"UPDATING DOC WITH ID "+"\033[0m",_id)
                print(f"\033[93m"+"NEW META "+"\033[0m",res['_meta'])
                self._doc.update(id=_id, refresh=True, _meta=res['_meta'] )
                status = (200,{'success': True, 'error': 'None'})
        else:
            status = (400,{'success': False, 'error': 'Invalid input data.'})

        return status

    # used in APIMetaDataHandler [DELETE]
    def delete_slug(self, _id, user, slug_name):
        ''' 
            delete the slug of API _id. 
            UPDATED TO DSL
        '''
        if not self.exists(_id):
            return (404, {"success": False, "error": "Could not retrieve API '{}' to delete slug name".format(_id)})

        i = API_Doc.get(id=_id).to_dict()
        _user = i.get('_meta', {}).get('github_username', '')

        # Make sure this is the correct user
        if user.get('login', None) != _user:
            return (405, {"success": False, "error": "User '{}' is not the owner of API '{}'".format(user.get('login', None), _id)})

        # Make sure this is the correct slug name
        if self._doc.to_dict().get('_meta', {}).get('slug', '') != slug_name:
            return (405, {"success": False, "error": "API '{}' slug name is not '{}'".format(_id, slug_name)})

        self._doc.update(id=_id, refresh=True, _meta={"slug":""} )

        return (200, {"success": True, "{}".format(_id): "slug '{}' deleted".format(slug_name)})