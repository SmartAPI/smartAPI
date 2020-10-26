"""
Controller for API docs

[APIHandler]
add - save doc

[APIMetaDataHandler]
get_api - get doc by name/slug
refresh_api - refresh api metadata
delete_slug - delete registered slug
update - save new slug
    _validate_slug_name - check slugname

[ValueSuggestionHandler]
get_tags - get list of tags/authors
"""

import logging
import string
from datetime import datetime as dt

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q, Index
from ..model.api_doc import API_Doc
from ..transform import (APIMetadata, decode_raw, get_api_metadata_by_url)
from tornado.httpclient import HTTPError

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    pass


class APIMetadataRegistrationError(Exception):
    pass


class APIDocController:

    def __init__(self, _id=None):
        doc = API_Doc()
        self._doc = doc.get(id=_id)

    @staticmethod
    def exists(_id):
        """
        Args:
            _id : id of metadata doc to be potentialy added

        Returns:
            Bool = exists?
        """
        doc = API_Doc()
        return doc.exists(_id=_id)

    @staticmethod
    def add(api_doc, save_v2=False, overwrite=False, user_name=None,
            override_owner=False, warn_on_identical=False, dryrun=False):
        """
        Validate metadata provided against openapi or swagger schema
        Check if document exists then
        Check if overwrite settings exist then
        Check if if its just a test run if not
        Save Doc

        Args:
            api_doc (dict): [API metadata]
            save_v2 (bool, optional): [save outdated version]. Defaults to False.
            overwrite (bool, optional): [overwrite existing doc]. Defaults to False.
            user_name (str, optional): [user.login]. Defaults to None.
            override_owner (bool, optional): [overwite owner]. Defaults to False.
            warn_on_identical (bool, optional): [warn on exact match found]. Defaults to False.
            dryrun (bool, optional): [test registration]. Defaults to False.

        Raises:
            RequestError: ES error while parsing request

        Returns:
            Returns True if this operation resulted in a new document being created.
        """
        metadata = APIMetadata(api_doc)
        # validate document schema
        validation = metadata.validate(raise_error_on_v2=not save_v2)
        if not validation['valid']:
            validation['success'] = False
            validation['error'] = '[Validation] ' + validation['error']
            # return valid
            return validation

        # generates an id based on source url
        api_id = metadata.encode_api_id()
        doc = API_Doc()
        doc_exists = doc.exists(api_id)
        # print("\033[93m"+"API EXISTS: "+"\033[0m", doc_exists)
        if doc_exists:
            if not overwrite:
                # print("\033[93m"+"NOT!!! OVERWRITE: "+"\033[0m", overwrite)
                return {"success": False, "error": "[Conflict] API exists. Not saved."}
            elif not override_owner:
                # Check user is owner
                i = API_Doc.get(id=api_id).to_dict()
                _owner = i.get('_meta', {}).get('github_username', '')
                if _owner != user_name:
                    return {"success": False, '_id': api_id, "error": "[Conflict] User mismatch. Not Saved."}

        # save to es index
        if dryrun:
            print("\033[93m"+"IS DRYRUN: "+"\033[0m", dryrun)
            return {"success": True, '_id': "[Dryrun] this is a dryrun. API is not saved.", "dryrun": True}

        try:
            doc = API_Doc(meta={'id': api_id}, ** metadata.convert_es())
            doc.save()
        except RequestError as e:
            return {"success": False, "error": "[ES]" + str(e)}
        else:
            return {"success": True, '_id': api_id}

    @staticmethod
    def get_api(api_name, fields=None, with_meta=True, return_raw=False, size=None, from_=0):
        """
        Used by Swagger UI to get doc metadata
        Ssed to get one specific doc by id/name/slug or get all

        Args:
            api_name (str): id,name, or slug
            fields (list, optional): fields to return if not all
            with_meta (bool, optional): Return _meta field. Defaults to True.
            return_raw (bool, optional): return raw. Defaults to False.
            size (int, optional): size of results. Defaults to None. No longer used.
            from_ (int, optional): start of returned results. Defaults to 0.
        Raises:
            ValueError: invalid input

        Returns:
            One API doc with metadata by default.
        """

        def _get_hit_object(hit):
            """[summary]

            Args:
                hit (list): ES reponse, list of hits

            Returns:
                dict: extracted doc dict
            """
            obj = hit.get('fields', hit.get('_source', {}))
            if '_id' in hit:
                obj['_id'] = hit['_id']
            return obj

        def _get_api_doc(api_doc, with_meta=True):
            doc = decode_raw(api_doc.get('~raw', ''))
            if with_meta:
                doc["_meta"] = api_doc.get('_meta', {})
                doc["_id"] = api_doc["_id"]
            return doc

        client = Elasticsearch()
        s = Search(using=client)
        if not fields:
            fields = ['_all']

        if api_name == 'all':
            total = s.count()
            start = 0
            if from_:
                start = from_
            s = s[start:total]
            # TODO fix specific fields in response
            s.source(includes=fields)
        else:
            # TODO fix specific fields in response
            s.source(includes=fields)
            s.query = Q('bool', should=[Q('match', _id=api_name) | Q('term', _meta__slug=api_name)], minimum_should_match=1)
        res = s.execute().to_dict()
        if return_raw == '2':
            return res
        res = [_get_hit_object(d) for d in res['hits']['hits']]
        if not return_raw:
            try:
                res = [_get_api_doc(x, with_meta=with_meta) for x in res]
            except ValueError as e:
                res = {'success': False, 'error': str(e)}
        if len(res) == 1:
            res = res[0]
        return res

    def get_tags(field=None, size=100):
        """
        perform aggregations on given field
        Used to generate list of tags and authors

        Args:
            field (str, optional): field name of doc. Defaults to None.
            size (int, optional): size returned. Defaults to 100.

        Returns:
            list of tags/authors name:occurrence or false
        """
        agg_name = 'field_values'
        doc = API_Doc()
        res = doc.aggregate(field=field, size=size, agg_name=agg_name)
        if res:
            return res.to_dict()
        else:
            return False

    def delete(self, _id, user):
        """
        delete api from index

        Args:
            _id (str): ID of doc
            user (str): user info of requester

        Returns:
            Success res if successful
        """
        doc = API_Doc.get(id=_id).to_dict()
        _user = doc.get('_meta', {}).get('github_username', '')

        # Make sure this is the correct user
        if user.get('login', None) != _user:
            return (405, {"success": False, "error": "User '{}' is not the owner of API '{}'".format(user.get('login', None), _id)})

        self._doc.delete(id=_id)
        Index(API_Doc.Index.name).refresh()
        return (200, {"success": True})

    def update(self, _id, user, slug_name):
        """
        Update API doc slug name

        Args:
            _id (str): doc ID to be updated
            user (dict): user info of requester
            slug_name (str): new slug name

        Raises:
            HTTPError: Doc does not exist
            HTTPError: User is not owner of doc
            HTTPError: General error parsing request

        Returns:
            Success res if updated
        """
        if not self.exists(_id):
            raise HTTPError(code=404,
                            response={'success': False,
                                      'error': "Could not retrieve API '{}' to set slug name".format(_id)})

        i = API_Doc.get(id=_id).to_dict()
        _user = i.get('_meta', {}).get('github_username', '')

        # Make sure this is the correct user
        if user.get('login', None) != _user:
            raise HTTPError(code=405,
                            response={'success': False,
                                      'error': "User '{}' is not the owner of API '{}'".format(user.get('login', None), _id)})

        # validate the slug name
        valid = self._validate_slug_name(slug_name=slug_name)

        if valid:
            try:
                doc = API_Doc()
                doc = doc.get(id=_id)
                doc.update(id=_id, refresh=True, _meta={"slug": slug_name.lower()})
            except Exception as exc:
                raise HTTPError(500, reason=str(exc))
            else:
                return (200, {"success": True, "{}._meta.slug".format(_id): slug_name.lower()})

    def _validate_slug_name(self, slug_name):
        """
        Function that determines whether slug_name is a valid slug name

        Args:
            slug_name (str): new slug name

        Raises:
            HTTPError: slug is a reserved word
            HTTPError: slug is not correct length
            HTTPError: slug has invalid characters

        Returns:
            True if available
        """
        _valid_chars = string.ascii_letters + string.digits + "-_~"
        _slug = slug_name.lower()
        # reserved for dev node, normal web functioning
        if _slug in ['www', 'dev', 'smart-api']:
            raise HTTPError(code=405,
                            response={'success': False,
                                      'error': "Slug name '{}' is reserved, please choose another".format(_slug)})
        # length requirements
        if len(_slug) < 4 or len(_slug) > 50:
            # return (False, {"success": False, "error": "Slug name must be between 4 and 50 chars"})
            raise HTTPError(code=405,
                            response={'success': False,
                                      'error': "Slug name must be between 4 and 50 chars"})
        # character requirements
        if not all([x in _valid_chars for x in _slug]):
            raise HTTPError(code=405,
                            response={'success': False,
                                      'error': "Slug name contains invalid characters.  Valid characters: '{}'".format(_valid_chars)})
        # does it exist already?
        doc = API_Doc()
        if doc.slug_exists(slug=_slug):
            raise HTTPError(code=405,
                            response={'success': False,
                                      'error': "Slug name '{}' already exists, please choose another".format(_slug)})
        # good name
        return True

    def refresh_api(self, _id, user):
        """
        refresh the given API document object based on its saved metadata url

        Args:
            _id (str): ID of API doc
            user (dict): user info

        Returns:
            Bool = updated?
        """

        api_doc = self._doc.to_dict()

        _meta = api_doc.get('_meta', {})

        res = get_api_metadata_by_url(_meta['url'])

        if res and isinstance(res, dict):
            if res.get('success', None) is False:
                res['error'] = '[Request] '+res.get('error', '')
                status = res
            else:
                _meta['timestamp'] = dt.now().isoformat()
                res['_meta'] = _meta
                print("\033[93m"+"UPDATING DOC WITH ID "+"\033[0m", _id)
                print("\033[93m"+"NEW META "+"\033[0m", res['_meta'])
                self._doc.update(id=_id, refresh=True, _meta=res['_meta'])
                status = (200, {'success': True, 'error': 'None'})
        else:
            status = (400, {'success': False, 'error': 'Invalid input data.'})

        return status

    def delete_slug(self, _id, user, slug_name):
        """
        delete the slug of API _id.
        used in APIMetaDataHandler [DELETE]

        Args:
            _id (str): ID of doc
            user (dict): user info of requester
            slug_name (str): slug name registered

        Returns:
            Bool = deleted?
        """
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

        self._doc.update(id=_id, refresh=True, _meta={"slug": ""})

        return (200, {"success": True, "{}".format(_id): "slug '{}' deleted".format(slug_name)})
