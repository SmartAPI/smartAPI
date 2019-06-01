#pylint: disable=unexpected-keyword-arg
# non-essential parameters are declared with decorators in es.py
# https://github.com/elastic/elasticsearch-py/issues/274

import json
import logging
import string
import sys
from datetime import date, datetime
from shlex import shlex

import boto3
from elasticsearch import Elasticsearch, RequestError, helpers

from .mapping import smart_api_mapping
from .transform import (SWAGGER2_INDEXED_ITEMS, APIMetadata, decode_raw,
                        get_api_metadata_by_url, polite_requests)

ES_HOST = 'localhost:9200'
ES_INDEX_NAME = 'smartapi_oas3'
ES_DOC_TYPE = 'api'


def ask(prompt, options='YN'):
    '''Prompt Yes or No,return the upper case 'Y' or 'N'.'''
    options = options.upper()
    while 1:
        s = input(prompt+'[%s]' % '|'.join(list(options))).strip().upper()
        if s in options:
            break
    return s


def get_datestamp():
    d = date.today()
    return d.strftime('%Y%m%d')


def get_es(es_host=None):
    es_host = es_host or ES_HOST
    es = Elasticsearch(es_host, timeout=120)
    return es


def split_ids(q):
    '''split input query string into list of ids.
       any of " \t\n\x0b\x0c\r|,+" as the separator,
        but perserving a phrase if quoted
        (either single or double quoted)
        more detailed rules see:
        http://docs.python.org/2/library/shlex.html#parsing-rules

        e.g. split_ids('CDK2 CDK3') --> ['CDK2', 'CDK3']
             split_ids('"CDK2 CDK3"\n CDk4')  --> ['CDK2 CDK3', 'CDK4']

    '''
    # Python3 strings are already unicode, .encode
    # now returns a bytearray, which cannot be searched with
    # shlex.  For now, do this terrible thing until we discuss
    if sys.version_info.major == 3:
        lex = shlex(q, posix=True)
    else:
        lex = shlex(q.encode('utf8'), posix=True)
    lex.whitespace = ' \t\n\x0b\x0c\r|,+'
    lex.whitespace_split = True
    lex.commenters = ''
    if sys.version_info.major == 3:
        ids = [x.strip() for x in list(lex)]
    else:
        ids = [x.decode('utf8').strip() for x in list(lex)]
    ids = [x for x in ids if x]
    return ids


def create_index(index_name=None, es=None):
    index_name = index_name or ES_INDEX_NAME
    body = {}
    mapping = {"mappings": smart_api_mapping}
    body.update(mapping)
    _es = es or get_es()
    print(_es.indices.create(index=index_name, body=body), end=" ")


def _get_hit_object(hit):
    obj = hit.get('fields', hit.get('_source', {}))
    if '_id' in hit:
        obj['_id'] = hit['_id']
    return obj


class ESQuery():
    def __init__(self, index=None, doc_type=None, es_host=None):
        self._es = get_es(es_host)
        self._index = index or ES_INDEX_NAME
        self._doc_type = doc_type or ES_DOC_TYPE

    def exists(self, api_id):
        '''return True/False if the input api_doc has existing metadata
           object in the index.
        '''
        return self._es.exists(index=self._index, doc_type=self._doc_type, id=api_id)

    # used in APIHandler [POST]
    def save_api(self, api_doc, save_v2=False, overwrite=False, user_name=None,
                 override_owner=False, warn_on_identical=False, dryrun=False):
        '''Adds or updates a compatible-format API document in the SmartAPI index, making it searchable.
        :param save_v2: allow a swagger v2 document pass validation when set to True
        :param overwrite: allow overwriting an existing document if the user_name provided matches the record
        :param user_name: when overwrite is set to to true, and override_owner not, 
            to allow overwriting the existing document user_name must match that of the document.
        :param override_owner: allow overwriting regardless of ownership when overwrite is also set to True
        :param warn_on_identical: consider rewriting the existing docuement with an identical one unsuccessful
            used in refresh_all() to exclude APIs with no change from update count
        :param dryrun: only validate the schema and test the overwrite settings, do not actually save.
        '''
        metadata = APIMetadata(api_doc)

        # validate document schema
        valid = metadata.validate(raise_error_on_v2=not save_v2)
        if not valid['valid']:
            valid['success'] = False
            valid['error'] = '[Validation] ' + valid['error']
            return valid

        # avoid unintended overwrite
        api_id = metadata.encode_api_id()
        doc_exists = self.exists(api_id)
        if doc_exists:
            if not overwrite:
                is_archived = self._es.get(
                    index=self._index, doc_type=self._doc_type, id=api_id, _source=["_meta"]).get(
                    '_source', {}).get(
                    '_meta', {}).get(
                    '_archived', False) == 'true'
                if not is_archived:
                    return {"success": False, "error": "[Conflict] API exists. Not saved."}
            elif not override_owner:
                _owner = self._es.get(
                    index=self._index, doc_type=self._doc_type, id=api_id, _source=["_meta"]).get(
                    '_source', {}).get(
                    '_meta', {}).get(
                    'github_username', '')
                if _owner != user_name:
                    return {"success": False, "error": "[Conflict] User mismatch. Not Saved."}

        # identical document
        _doc = metadata.convert_es()
        if doc_exists:
            _raw_stored = self._es.get(
                index=self._index, doc_type=self._doc_type, id=api_id, _source=["~raw"]).get(
                '_source', {})['~raw']
            if decode_raw(
                    _raw_stored, as_string=True) == decode_raw(
                    _doc.get('~raw'),
                    as_string=True):
                if warn_on_identical:
                    return {"success": True, '_id': api_id, "warning": "[Conflict] No change in document."}
                else:
                    return {"success": True, '_id': api_id}

        # save to es index
        if dryrun:
            return {"success": True, '_id': "[Dryrun] this is a dryrun. API is not saved.", "dryrun": True}
        try:
            self._es.index(index=self._index, doc_type=self._doc_type,
                           body=_doc, id=api_id, refresh=True)
        except RequestError as e:
            return {"success": False, "error": "[ES]" + str(e)}
        return {"success": True, '_id': api_id}

    def _get_api_doc(self, api_doc, with_meta=True):
        doc = decode_raw(api_doc.get('~raw', ''))
        if with_meta:
            doc["_meta"] = api_doc.get('_meta', {})
            doc["_id"] = api_doc["_id"]
        return doc

    # used in APIMetaDataHandler [GET]
    def get_api(self, api_name, fields=None, with_meta=True, return_raw=False, size=None, from_=0):
        if api_name == 'all':
            query = {'query': {"bool": {"must_not": {
                "term": {"_meta._archived": "true"}}}}}
        else:
            query = {
                "query": {
                    "bool": {
                        "should": [
                            {
                                "match": {
                                    "_id": {
                                        "query": api_name
                                    }
                                }
                            },
                            {
                                "term": {
                                    "_meta.slug": api_name
                                }
                            }
                        ],
                        "must_not": {"term": {"_meta._archived": "true"}}
                    }
                }
            }
        if fields and fields not in ["all", ["all"]]:
            query["_source"] = fields
        if size and isinstance(size, int):
            query['size'] = min(size, 100)    # set max size to 100 for now.
        if from_ and isinstance(from_, int) and from_ > 0:
            query['from'] = from_
        res = self._es.search(self._index, self._doc_type, query)
        if return_raw == '2':
            return res
        res = [_get_hit_object(d) for d in res['hits']['hits']]
        if not return_raw:
            try:
                res = [self._get_api_doc(x, with_meta=with_meta) for x in res]
            except ValueError as e:
                res = {'success': False, 'error': str(e)}
        if len(res) == 1:
            res = res[0]
        return res

    def _do_aggregations(self, _field, agg_name, size):
        query = {
            "query": {
                "bool": {
                    "must_not": {"term": {"_meta._archived": True}}
                }
            },
            "aggs": {
                agg_name: {
                    "terms": {
                        "field": _field,
                        "size": size
                    }
                }
            }
        }
        res = self._es.search(self._index, self._doc_type, query, size=0)
        res = res["aggregations"]
        return res

    def get_api_id_from_slug(self, slug_name):
        query = {
            "query": {
                "bool": {
                    "should": [
                        {"term": {"_meta.slug": slug_name}},
                        {"ids": {"values": [slug_name]}}
                    ]
                }
            }
        }
        try:
            res = self._es.search(
                index=self._index, doc_type=self._doc_type, body=query, size=1, _source=False)
        except:
            return
        if res.get('hits', {}).get('hits', []):
            return res['hits']['hits'][0]['_id']

    # used in ValueSuggestionHandler [GET]
    def value_suggestion(self, field, size=100, use_raw=True):
        """return a list of existing values for the given field."""
        _field = field + ".raw" if use_raw else field
        agg_name = 'field_values'
        res = self._do_aggregations(_field, agg_name, size)
        return res

    def delete_api(self, id):
        """delete a saved API metadata, be careful with the deletion."""
        if ask("Are you sure to delete this API metadata?") == 'Y':
            print(self._es.delete(index=self._index,
                                  doc_type=self._doc_type, id=id))

    # used in APIMetaDataHandler [DELETE]
    def archive_api(self, id, user):
        """ function to set an _archive flag for an API, making it
        unsearchable from the front end, takes an id identifying the API,
        and a user that must match the APIs creator. """
        # does the api exist?
        try:
            _doc = self._es.get(index=self._index,
                                doc_type=self._doc_type, id=id)
        except:
            _doc = None
        if not _doc:
            return (404, {"success": False, "error": "Could not retrieve API '{}' to delete".format(id)})
        # is the api unarchived?
        if _doc.get('_source', {}).get('_meta', {}).get('_archived', False):
            return (405, {"success": False, "error": "API '{}' already deleted".format(id)})
        # is this user the owner of this api?
        _user = user.get('login', None)
        if _doc.get('_source', {}).get('_meta', {}).get('github_username', '') != _user:
            return (405, {"success": False, "error": "User '{user}' is not the owner of API '{id}'".format(user=_user, id=id)})
        # do the archive, deregister the slug name
        _doc['_source']['_meta']['_archived'] = 'true'
        _doc['_source']['_meta'].pop('slug', None)
        self._es.index(index=self._index, doc_type=self._doc_type,
                       id=id, body=_doc['_source'], refresh=True)

        return (200, {"success": True, "message": "API '{}' successfully deleted".format(id)})

    # used in GitWebhookHandler [POST] and self.backup_all()
    def fetch_all(self, as_list=False, id_list=[], query={}, ignore_archives=False):
        """return a generator of all docs from the ES index.
            return a list instead if as_list is True.
            if query is passed, it returns docs that match the query.
            else if id_list is passed, it returns only docs from the given ids.
        """
        if query:
            _query = query
        elif id_list:
            _query = {"query": {"ids": {"type": ES_DOC_TYPE, "values": id_list}}}
        elif ignore_archives:
            _query = {"query": {"bool": {"must_not": {"term": {"_meta._archived": "true"}}}}}
        else:
            _query = {"query": {"match_all": {}}}

        scan_res = helpers.scan(client=self._es, query=_query,
                                index=self._index, doc_type=self._doc_type)

        def _fn(x):
            x['_source'].setdefault('_id', x['_id'])
            return x['_source']
        doc_iter = (_fn(x) for x in scan_res)    # return docs only
        if as_list:
            return list(doc_iter)
        else:
            return doc_iter

    def backup_all(self, outfile=None, ignore_archives=False, aws_s3_bucket=None):
        """back up all docs into a output file."""
        # get the real index name in case self._index is an alias
        logging.info("Backup started.")
        alias_d = self._es.indices.get_alias(self._index)
        assert len(alias_d) == 1
        index_name = list(alias_d.keys())[0]
        default_name = "{}_backup_{}.json".format(index_name, get_datestamp())
        outfile = outfile or default_name
        doc_li = self.fetch_all(as_list=True, ignore_archives=ignore_archives)
        if aws_s3_bucket:
            location_prompt = 'on S3'
            s3 = boto3.resource('s3')
            s3.Bucket(aws_s3_bucket).put_object(
                Key='db_backup/{}'.format(outfile), Body=json.dumps(doc_li, indent=2))
        else:
            out_f = open(outfile, 'w')
            location_prompt = 'locally'
            out_f = open(outfile, 'w')
            json.dump(doc_li, out_f, indent=2)
            out_f.close()
        logging.info("Backed up %s docs in \"%s\" %s.", len(doc_li), outfile, location_prompt)

    def restore_all(self, backupfile, index_name, overwrite=False):
        """restore all docs from the backup file to a new index."""

        def legacy_backupfile_support_path_str(_doc):
            _paths = []
            if 'paths' in _doc:
                for path in _doc['paths']:
                    _paths.append({
                        "path": path,
                        "pathitem": _doc['paths'][path]
                    })
            if _paths:
                _doc['paths'] = _paths
            return _doc

        def legacy_backupfile_support_rm_flds(_doc):
            _d = {"_meta": _doc['_meta']}
            for key in SWAGGER2_INDEXED_ITEMS:
                if key in _doc:
                    _d[key] = _doc[key]
            _d['~raw'] = _doc['~raw']
            return _d

        if self._es.indices.exists(index_name):
            if overwrite and ask("Warning: index \"{}\" exists. Do you want to overwrite it?".format(index_name)) == 'Y':
                self._es.indices.delete(index=index_name)
            else:
                print(
                    "Error: index \"{}\" exists. Try a different index_name.".format(index_name))
                return

        print("Loading docs from \"{}\"...".format(backupfile), end=" ")
        in_f = open(backupfile)
        doc_li = json.load(in_f)
        print("Done. [{} Documents]".format(len(doc_li)))

        print("Creating index...", end=" ")
        create_index(index_name, es=self._es)
        print("Done.")

        print("Indexing...", end=" ")
        swagger_v2_count = 0
        openapi_v3_count = 0
        for _doc in doc_li:
            _id = _doc.pop('_id')
            if "swagger" in _doc:
                swagger_v2_count += 1
                _doc = legacy_backupfile_support_rm_flds(_doc)
                _doc = legacy_backupfile_support_path_str(_doc)
            elif "openapi" in _doc:
                openapi_v3_count += 1
            else:
                print('\n\tWARNING: ', _id, 'No Version.')
            self._es.index(index=index_name,
                           doc_type=self._doc_type, body=_doc, id=_id)
        print(swagger_v2_count, ' Swagger Objects and ',
              openapi_v3_count, ' Openapi Objects. ')
        print("Done.")

    def _validate_slug_name(self, slug_name):
        ''' Function that determines whether slug_name is a valid slug name '''
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
        _query = {
            "query": {
                "bool": {
                    "should": [
                        {"term": {"_meta.slug.raw": _slug}},
                        {"ids": {"values": [_slug]}}
                    ]
                }
            }
        }

        if len(
            self._es.search(
                index=self._index, doc_type=self._doc_type, body=_query, _source=False).get(
                'hits', {}).get('hits', [])) > 0:
            return (False, {"success": False, "error": "Slug name '{}' already exists, please choose another".format(_slug)})

        # good name
        return (True, {})

    # used in APIMetaDataHandler [PUT]
    def set_slug_name(self, _id, user, slug_name):
        ''' set the slug name of API _id to slug_name. '''
        if not self.exists(_id):
            return (404, {"success": False, "error": "Could not retrieve API '{}' to set slug name".format(_id)})

        _user = self._es.get(
            index=self._index, doc_type=self._doc_type, id=_id, _source=["_meta"]).get(
            '_source', {}).get(
            '_meta', {}).get(
            'github_username', '')

        # Make sure this is the correct user
        if user.get('login', None) != _user:
            return (405, {"success": False, "error": "User '{}' is not the owner of API '{}'".format(user.get('login', None), _id)})

        # validate the slug name
        _valid, _resp = self._validate_slug_name(slug_name=slug_name)

        if not _valid:
            return (405, _resp)

        # update the slug name
        self._es.update(index=self._index, doc_type=self._doc_type, id=_id, body={
                        "doc": {"_meta": {"slug": slug_name.lower()}}}, refresh=True)

        return (200, {"success": True, "{}._meta.slug".format(_id): slug_name.lower()})

    # used in APIMetaDataHandler [DELETE]
    def delete_slug(self, _id, user, slug_name):
        ''' delete the slug of API _id. '''
        if not self.exists(_id):
            return (404, {"success": False, "error": "Could not retrieve API '{}' to delete slug name".format(_id)})

        doc = self._es.get(index=self._index,
                           doc_type=self._doc_type, id=_id).get('_source', {})

        # Make sure this is the correct user
        if user.get('login', None) != doc.get('_meta', {}).get('github_username', ''):
            return (405, {"success": False, "error": "User '{}' is not the owner of API '{}'".format(user.get('login', None), _id)})

        # Make sure this is the correct slug name
        if doc.get('_meta', {}).get('slug', '') != slug_name:
            return (405, {"success": False, "error": "API '{}' slug name is not '{}'".format(_id, slug_name)})

        # do the delete
        doc['_meta'].pop('slug')

        self._es.index(index=self._index, doc_type=self._doc_type,
                       body=doc, id=_id, refresh=True)

        return (200, {"success": True, "{}".format(_id): "slug '{}' deleted".format(slug_name)})

    # used in APIMetaDataHandler [PUT]
    def refresh_one_api(self, _id, user, dryrun=True):
        ''' authenticate the API document of specified _id correspond to the specified user,
            and refresh the API document based on its saved metadata url '''

        # _id validation
        try:
            api_doc = self._es.get(
                index=self._index, doc_type=self._doc_type, id=_id)
        except:
            return (404, {"success": False, "error": "Could not retrieve API '{}' to refresh".format(_id)})
        api_doc['_source'].update({'_id': api_doc['_id']})

        # ownership validation
        _user = user.get('login', None)
        if api_doc.get('_source', {}).get('_meta', {}).get('github_username', '') != _user:
            return (405, {"success": False, "error": "User '{user}' is not the owner of API '{id}'".format(user=_user, id=_id)})

        status = self._refresh_one(
            api_doc=api_doc['_source'], user=_user, dryrun=dryrun)
        if not dryrun:
            self._es.indices.refresh(index=self._index)

        if status.get('success', False):
            return (200, status)
        else:
            return (405, status)

    def _refresh_one(self, api_doc, user=None, override_owner=False, dryrun=True,
                     error_on_identical=False, save_v2=False):
        ''' refresh the given API document object based on its saved metadata url  '''
        _id = api_doc['_id']
        _meta = api_doc['_meta']

        res = get_api_metadata_by_url(_meta['url'])
        if res and isinstance(res, dict):
            if res.get('success', None) is False:
                res['error'] = '[Request] '+res.get('error', '')
                status = res
            else:
                _meta['timestamp'] = datetime.now().isoformat()
                res['_meta'] = _meta
                status = self.save_api(
                    res, user_name=user, override_owner=override_owner, overwrite=True,
                    dryrun=dryrun, warn_on_identical=error_on_identical, save_v2=True)
        else:
            status = {'success': False, 'error': 'Invalid input data.'}

        return status

    def refresh_all(
            self, id_list=[],
            dryrun=True, return_status=False, use_etag=True, ignore_archives=True):
        '''refresh saved API documents based on their metadata urls.

        :param id_list: the list of API documents to perform the refresh operation
        :param ignore_archives:
        :param dryrun: 
        :param use_etag: by default, HTTP ETag is used to speed up version detection
        '''
        updates = 0
        status_li = []
        logging.info("Refreshing API metadata:")

        for api_doc in self.fetch_all(id_list=id_list, ignore_archives=ignore_archives):

            _id, status = api_doc['_id'], ''

            if use_etag:
                _res = polite_requests(api_doc.get('_meta', {}).get('url', ''), head=True)
                if _res.get('success'):
                    res = _res.get('response')
                    etag_local = api_doc.get('_meta', {}).get('ETag', '')
                    etag_server = res.headers.get('ETag', 'N').strip('W/"')
                    if etag_local == etag_server:
                        status = "OK (Via Etag)"

            if not status:
                res = self._refresh_one(
                    api_doc, dryrun=dryrun, override_owner=True, error_on_identical=True,
                    save_v2=True)
                if res.get('success'):
                    if res.get('warning'):
                        status = 'OK'
                    else:
                        status = "OK Updated"
                        updates += 1
                else:
                    status = "ERR " + res.get('error')[:60]

            status_li.append((_id, status))
            logging.info("%s: %s", _id, status)

        logging.info("%s: %s APIs refreshed. %s Updates.", get_datestamp(), len(status_li), updates)

        if dryrun:
            logging.warning("This is a dryrun! No actual changes have been made.")
            logging.warning("When ready, run it again with \"dryrun=False\" to apply changes.")

        return status_li
