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

from elasticsearch import RequestError
from elasticsearch_dsl import Search, Q
from ..model.api_doc import API_Doc
from ..transform import (APIMetadata, decode_raw, get_api_metadata_by_url)

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
    def add(api_doc, save_v2=False, overwrite=False, user_name=None, dryrun=False, url=None):
        """
        APIMetadata Class validates doc for supported OAS3 or V2 (warning)
        and generates an id based on source url
        Check if document exists then
        Error details will be returned in 'because' field
        Save Doc if passes all checks

        Args:
            api_doc (dict): [API metadata]
            save_v2 (bool, optional): [save outdated version]. Defaults to False.
            overwrite (bool, optional): [overwrite existing doc]. Defaults to False.
            user_name (str, optional): [user.login]. Defaults to None.
            dryrun (bool, optional): [test registration]. Defaults to False.

        Returns:
            Returns generated API ID if this operation resulted in a new document being saved.
        """
        api_doc['_meta'] = {
            "github_username": user_name,
            'url': url,
            'timestamp': dt.now().isoformat()
        }
        metadata = APIMetadata(api_doc)
        validation = metadata.validate()
        if validation.get('valid') is False:
            return validation
        if validation.get('v2') is True and not save_v2:
            return {'because': 'API is Swagger V2 which is not fully suppported'}
        api_id = metadata.encode_api_id()
        doc_exists = API_Doc.exists(api_id)
        if doc_exists and not overwrite:
            raise APIMetadataRegistrationError('API Exists')
            # return {'because': 'API Exists'}
        if dryrun:
            return {'because': 'API is valid but this was only a test'}
        try:
            doc = API_Doc(meta={'id': api_id}, ** metadata.convert_es())
            doc.save()
        except RequestError as e:
            return {"because": "[ES]" + str(e)}
        else:
            return {'_id': api_id}

    @staticmethod
    def get_api(api_name, fields=None, with_meta=True, return_raw=False, size=None, from_=0):
        """
        Used by Swagger UI to get doc metadata
        Used to get one specific doc by id/name/slug or get all

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
                hit (list): ES response, list of hits

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

        # client = Elasticsearch()
        # s = Search(using=client)
        s = API_Doc.search()
        # change to higher level client
        if not fields:
            fields = ['_all']

        if api_name == 'all':
            total = s.count()
            start = 0
            if from_:
                start = from_
            s = s[start:total]
            s.source(includes=fields)
        else:
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
        res = API_Doc.aggregate(field=field, size=size, agg_name=agg_name)
        if res:
            return res.to_dict()
        else:
            return False

    def delete(self, _id, user):
        """
        delete api by current user
        refresh index after deletion and return true

        Args:
            _id (str): ID of doc
            user (str): user info of requester

        Returns:
            Success res if successful
        """
        doc = API_Doc.get(id=_id).to_dict()
        _user = doc.get('_meta', {}).get('github_username', '')

        if user.get('login', None) != _user:
            return {"because": "User '{}' is not the owner of API '{}'".format(user.get('login', None), _id)}

        self._doc.delete(id=_id)
        return {"deleted": True}

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
        if not API_Doc.exists(_id):
            return {'because': "Could not retrieve API '{}' to set slug name".format(_id)}

        i = API_Doc.get(id=_id).to_dict()
        _user = i.get('_meta', {}).get('github_username', '')

        # Make sure this is the correct user
        if user.get('login', None) != _user:
            return {'because': "User '{}' is not the owner of API '{}'".format(user.get('login', None), _id)}

        # validate the slug name
        validation = self._validate_slug_name(slug_name=slug_name)

        if 'success' in validation:
            try:
                doc = API_Doc()
                doc = doc.get(id=_id)
                doc.update(id=_id, refresh=True, _meta={"slug": slug_name.lower()})
            except Exception as exc:
                return {'because': "[Err]" + str(exc)}
                # raise HTTPError(500, reason=str(exc))
            else:
                return {"{}._meta.slug".format(_id): slug_name.lower()}
        else:
            return validation

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
        if _slug in ['www', 'dev', 'smart-api']:
            return {'because': f"Slug name {slug_name} is reserved, please choose another"}
        if len(_slug) < 4 or len(_slug) > 50:
            return {'because': f"Slug name {slug_name} must be between 4 and 50 chars"}
        if not all([x in _valid_chars for x in _slug]):
            return {'because': f"Slug name {slug_name} contains invalid characters"}
        if API_Doc.slug_exists(slug=_slug):
            return {'because': f"Slug name {slug_name} already exists"}
        return {'success': True}

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

        if 'because' in res:
            return res
        else:
            if res['metadata'] and isinstance(res['metadata'], dict):
                _meta['timestamp'] = dt.now().isoformat()
                res['metadata']['_meta'] = _meta
                self._doc.update(id=_id, refresh=True, _meta=res['metadata']['_meta'])
                return {'updated': f"API with ID {_id} was refreshed"}
            else:
                return {'because': 'Invalid input data.'}

    def delete_slug(self, _id, user, slug_name):
        """
        delete the slug of API _id.
        used in APIMetaDataHandler [DELETE]

        Args:
            _id (str): ID of doc
            user (dict): user info of requester
            slug_name (str): slug name registered
        """
        if not API_Doc.exists(_id):
            return {"because": "Could not retrieve API '{}' to delete slug name".format(_id)}

        i = API_Doc.get(id=_id).to_dict()
        _user = i.get('_meta', {}).get('github_username', '')

        # Make sure this is the correct user
        if user.get('login', None) != _user:
            return {"because": "User '{}' is not the owner of API '{}'".format(user.get('login', None), _id)}

        # Make sure this is the correct slug name
        if self._doc.to_dict().get('_meta', {}).get('slug', '') != slug_name:
            return {"because": "API '{}' slug name is not '{}'".format(_id, slug_name)}

        self._doc.update(id=_id, refresh=True, _meta={"slug": ""})

        return {"{}".format(_id): "slug '{}' deleted".format(slug_name)}
