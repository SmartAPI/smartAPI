import json
import string
import requests
import sys
from datetime import date, datetime
from shlex import shlex

from elasticsearch import Elasticsearch, RequestError, helpers

from .transform import APIMetadata, decode_raw, get_api_metadata_by_url

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
    mapping = {
        "api": {
            "dynamic_templates": [
                {
                    "ignore_example_field": {
                        "match": "example",
                        "mapping": {
                            "index": False
                        }
                    }
                },
                {
                    "ignore_ref_field": {
                        "match": "$ref",
                        "mapping": {
                            "index": False
                        }
                    }
                },
                {
                    "ignore_schema_field": {
                        "match": "schema",
                        "mapping": {
                            "enabled": False
                        }
                    }
                },
                {
                    "ignore_content_field": {
                        "match": "content",
                        "mapping": {
                            "enabled": False
                        }
                    }
                },
                # this must be the last template
                {
                    "template_1": {
                        "match": "*",
                        "match_mapping_type": "string",
                        "mapping": {
                            "type": "text",
                            "index": True,
                            "ignore_malformed": True,
                            "fields": {
                                "raw": {
                                    "type": "keyword"
                                }
                            }
                        }
                    }
                }
            ],
            "properties": {
                "components": {
                    "enabled": False
                },
                "definitions": {
                    "enabled": False
                },
                "~raw": {
                    "type": "binary"
                }
            }
        }
    }
    mapping = {"mappings": mapping}
    body.update(mapping)
    _es = es or get_es()
    print(_es.indices.create(index=index_name, body=body),end=" ")


# def _encode_api_object_id(api_doc):
    # info_d = api_doc.get('info', {})
    # api_title, api_version = info_d.get('title', ''), info_d.get('version', '')
    # api_contact = info_d.get('contact', {})
    # api_contact = api_contact.get('name', '')
    # if not (api_title and api_version and api_contact):
    #     raise ValueError("Missing required info fields.")
    # x = json.dumps((api_title, api_version, api_contact))
    # return blake2b(x.encode('utf8'), digest_size=16).hexdigest()


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

    def save_api(self, api_doc, user_name=None, override_owner=False, overwrite=False, dryrun=False, overwrite_if_identical=True, save_v2=False):
        metadata = APIMetadata(api_doc)
        valid = metadata.validate(raise_error_on_v2=not save_v2)
        if not valid['valid']:
            valid['success'] = False
            return valid

        api_id = metadata.encode_api_id()
        doc_exists = self.exists(api_id)
        #_raw = ""
        if doc_exists:
            if not overwrite:
                is_archived = self._es.get(index=self._index, doc_type=self._doc_type, id=api_id, _source=[
                                           "_meta"]).get('_source', {}).get('_meta', {}).get('_archived', False) == 'true'
                if not is_archived:
                    return {"success": False, "error": "API exists. Not saved."}
            elif not override_owner:
                _owner = self._es.get(index=self._index, doc_type=self._doc_type, id=api_id, _source=[
                                      "_meta"]).get('_source', {}).get('_meta', {}).get('github_username', '')
                if _owner != user_name:
                    return {"success": False, "error": "Cannot overwrite an API that doesn't belong to you"}
            #_raw = self._es.get(index=self._index, doc_type=self._doc_type, id=api_id, _source=["~raw"]).get('_source', {})['~raw']
        _doc = metadata.convert_es()
        if dryrun:
            return {"success": True, '_id': "this is a dryrun. API is not saved.", "dryrun": True}
        # if not overwrite_if_identical and decode_raw(_raw, as_string=True) == decode_raw(_doc.get('~raw'), as_string=True):
        #    print("No changes in _id {}".format(api_id))
        #    return {"success": True, '_id': "No changes in document."}
        try:
            self._es.index(index=self._index, doc_type=self._doc_type,
                           body=_doc, id=api_id, refresh=True)
        except RequestError as e:
            return {"success": False, "error": str(e)}
        return {"success": True, '_id': api_id}

    def _get_api_doc(self, api_doc, with_meta=True):
        doc = decode_raw(api_doc.get('~raw', ''))
        if with_meta:
            doc["_meta"] = api_doc.get('_meta', {})
            doc["_id"] = api_doc["_id"]
        return doc

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

    def query_api(self, q, filters=None, fields=None, return_raw=True, size=None, from_=0, raw_query=False):
        # query = {
        #     "query":{
        #         "match" : {
        #             attr: {
        #                 "query": q
        #             }
        #         }
        #     }
        # }
        try:
            query = json.loads(q)
            assert isinstance(query, dict)
            is_raw_query = True
        except (ValueError, AssertionError):
            is_raw_query = False

        if not is_raw_query:
            if q == '__all__':
                query = {
                    "query": {
                        "match_all": {}
                    }
                }
            else:
                query = {
                    "query": {
                        "dis_max": {
                            "queries": [
                                {
                                    "term": {
                                        "info.title": {
                                            "value": q,
                                            "boost": 2.0
                                        }
                                    }
                                },
                                {
                                    "term": {
                                        "server.url": {
                                            "value": q,
                                            "boost": 1.1
                                        }
                                    }
                                },
                                {
                                    "term": {
                                        "_id": q,
                                    }
                                },
                                {
                                    "query_string": {
                                        "query": q
                                    }
                                },
                                {
                                    "query_string": {
                                        "query": q + "*",
                                        "boost": 0.8
                                    }
                                },
                            ]
                        }
                    }
                }
                # query = {
                #     "query": {
                #         "query_string": {
                #             "query": q
                #         }
                #     }
                # }

        query = {
            "query": {
                "bool": {
                    "must": query["query"],
                    "must_not": {"term": {"_meta._archived": "true"}}
                }
            }
        }

        if filters:
            if len(filters) == 1:
                query["query"]["bool"]["filter"] = {"terms": filters}
            else:
                query["query"]["bool"]["filter"] = [
                    {"terms": {philter[0]:philter[1]}} for philter in filters.items()]

        if not fields or fields == 'all':
            pass
        else:
            try:
                _fields = split_ids(fields)
                query['_source'] = _fields
            except ValueError as e:
                # should pass errors back to handlers
                return {'success': False, 'error': 'Could not split "fields" argument due to the following error: "{}"'.format(str(e))}
        if size and isinstance(size, int):
            query['size'] = min(size, 100)    # set max size to 100 for now.
        if from_ and isinstance(from_, int) and from_ > 0:
            query['from'] = from_
        # else:
        #     query['_source'] = ['@id', attr_input, attr_output]
        # print(query)
        if raw_query:
            return query

        res = self._es.search(self._index, self._doc_type, body=query)
        if not return_raw:
            _res = res['hits']
            _res['took'] = res['took']
            if "aggregations" in res:
                _res['aggregations'] = res['aggregations']
            for v in _res['hits']:
                del v['_type']
                del v['_index']
                for attr in ['fields', '_source']:
                    if attr in v:
                        v.update(v[attr])
                        del v[attr]
                        break
            res = _res
        return res

    def _do_aggregations(self, _field, agg_name, size):
        query = {
            "query": {
                "bool": {
                    "must_not": {"term": {"_meta._archived": "true"}}
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

    def value_suggestion(self, field, size=100, use_raw=True):
        """return a list of existing values for the given field."""
        _field = field + ".raw" if use_raw else field
        agg_name = 'field_values'
        res = self._do_aggregations(_field, agg_name, size)
        if use_raw and not res[agg_name]['buckets']:
            # if *.raw does not return any buckets, try without it.
            res = self._do_aggregations(field, agg_name, size)

        return res

    def delete_api(self, id):
        """delete a saved API metadata, be careful with the deletion."""
        if ask("Are you sure to delete this API metadata?") == 'Y':
            print(self._es.delete(index=self._index,
                                  doc_type=self._doc_type, id=id))

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

    def fetch_all(self, as_list=False, id_list=[], query={}):
        """return a generator of all docs from the ES index.
            return a list instead if as_list is True.
            if query is passed, it returns docs that match the query.
            else if id_list is passed, it returns only docs from the given ids.
        """
        if query:
            _query = query
        elif id_list:
            _query = {"query": {"ids": {"type": ES_DOC_TYPE, "values": id_list}}}
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

    def backup_all(self, outfile=None):
        """back up all docs into a output file."""
        # get the real index name in case self._index is an alias
        alias_d = self._es.indices.get_alias(self._index)
        assert len(alias_d) == 1
        index_name = list(alias_d.keys())[0]
        outfile = outfile or "{}_backup_{}.json".format(
            index_name, get_datestamp())
        out_f = open(outfile, 'w')
        doc_li = self.fetch_all(as_list=True)
        json.dump(doc_li, out_f, indent=2)
        out_f.close()
        print("Backed up {} docs in \"{}\".".format(len(doc_li), outfile))

    def restore_all(self, backupfile, index_name):
        """restore all docs from the backup file to a new index.
           must restore to a new index, cannot overwrite an existing one.
        """
        if self._es.indices.exists(index_name):
            print(
                "Error: index \"{}\" exists. Try a different index_name.".format(index_name))
            return
            
        print("Loading docs from \"{}\"...".format(backupfile), end=" ")
        in_f = open(backupfile)
        doc_li = json.load(in_f)
        print("Done. [{}]".format(len(doc_li)))

        print("Creating index...", end=" ")
        create_index(index_name, es=self._es)
        print("Done.")

        print("Indexing...", end=" ")
        for _doc in doc_li:
            _id = _doc.pop('_id')
            
            # convert saved data to new format
            _paths = []
            for path in _doc['paths']:
                if "swagger" in _doc:
                    _paths.append({
                        "path": path,
                        "pathitem": _doc['paths'][path]
                    })
            if _paths:
                _doc['paths'] = _paths

            self._es.index(index=index_name,
                           doc_type=self._doc_type, body=_doc, id=_id)
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

        if len(self._es.search(index=self._index, doc_type=self._doc_type, body=_query, _source=False).get('hits', {}).get('hits', [])) > 0:
            return (False, {"success": False, "error": "Slug name '{}' already exists, please choose another".format(_slug)})

        # good name
        return (True, {})

    def set_slug_name(self, _id, user, slug_name):
        ''' set the slug name of API _id to slug_name. '''
        if not self.exists(_id):
            return (404, {"success": False, "error": "Could not retrieve API '{}' to set slug name".format(_id)})

        _user = self._es.get(index=self._index, doc_type=self._doc_type, id=_id, _source=[
                             "_meta"]).get('_source', {}).get('_meta', {}).get('github_username', '')

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

    def refresh_one_api(self, _id, user, dryrun=True):
        ''' refresh one API metadata based on the saved metadata url '''
        print("Refreshing API metadata:")
        try:
            api_doc = self._es.get(
                index=self._index, doc_type=self._doc_type, id=_id)
        except:
            return (404, {"success": False, "error": "Could not retrieve API '{}' to refresh".format(_id)})
        api_doc['_source'].update({'_id': api_doc['_id']})
        _user = user.get('login', None)
        if api_doc.get('_source', {}).get('_meta', {}).get('github_username', '') != _user:
            return (405, {"success": False, "error": "User '{user}' is not the owner of API '{id}'".format(user=_user, id=_id)})
        status = self._refresh_one(
            api_doc=api_doc['_source'], user=_user, dryrun=dryrun)
        print("="*25)
        if dryrun:
            print("This is a dryrun! No actual changes have been made.")
            print(
                "When ready, run it again with \"dryrun=False\" to apply actual changes.")
        else:
            self._es.indices.refresh(index=self._index)
        if status.get('success', False):
            print("Success.")
            return (200, status)
        else:
            print("Failed.")
            return (405, status)

    def _refresh_one(self, api_doc, user=None, override_owner=False, dryrun=True, overwrite_if_identical=True, save_v2=False):
        ''' refresh one API metadata based on the saved metadata url
            api_doc is the metadata document from ES '''
        _id = api_doc['_id']
        _meta = api_doc['_meta']
        print("\t{}...".format(_id), end='')
        new_api_doc = get_api_metadata_by_url(_meta['url'])
        if new_api_doc and isinstance(new_api_doc, dict):
            if new_api_doc.get('success', None) is False:
                status = new_api_doc
            else:
                _meta['timestamp'] = datetime.now().isoformat()
                new_api_doc['_meta'] = _meta
                status = self.save_api(new_api_doc, user_name=user, override_owner=override_owner, overwrite=True,
                                       dryrun=dryrun, overwrite_if_identical=overwrite_if_identical, save_v2=True)
        else:
            status = {'success': False, 'error': 'Invalid input data.'}

        return status

    def refresh_all(self, id_list=[], dryrun=True, return_status=False, overwrite_if_identical=False):
        '''refresh API metadata based on the saved metadata urls.'''
        success_cnt = 0
        total_cnt = 0
        if return_status:
            status_li = []
        print("Refreshing API metadata:")
        for api_doc in self.fetch_all(id_list=id_list):
            status = self._refresh_one(api_doc, dryrun=dryrun, override_owner=True,
                                       overwrite_if_identical=overwrite_if_identical, save_v2=True)
            if status.get('success', False):
                print("Success.")
                success_cnt += 1
            else:
                print("Failed.")
            total_cnt += 1
            if return_status:
                status_li.append((api_doc['_id'], status))
        print("="*25)
        print("Successfully refreshed {}/{} API meteadata.".format(success_cnt, total_cnt))
        if dryrun:
            print("This is a dryrun! No actual changes have been made.")
            print(
                "When ready, run it again with \"dryrun=False\" to apply actual changes.")
        if return_status:
            return status_li

    def cron_refresh(self, id_list=[]):
        '''refresh API metadata based on the saved metadata urls.'''
        print("Refreshing API metadata:")
        for api_doc in self.fetch_all(id_list=id_list):
            # print(api_doc.get('paths', {}))
            doc_etag = api_doc.get('_meta', {}).get('ETag', '')
            try:
                curr_etag = requests.get(api_doc.get('_meta', {}).get(
                    'url', '')).headers.get('ETag', 'N').strip('W/"')
            except:
                print("Error retrieving metadata doc for API {}".format(
                    api_doc.get('_id', '')))
            if doc_etag != curr_etag:
                # doc changed...
                _meta = api_doc['_meta']
                print("\t{}...".format(api_doc['_id']), end='')
                new_api_doc = get_api_metadata_by_url(_meta['url'])
                if new_api_doc and isinstance(new_api_doc, dict):
                    if new_api_doc.get('success', None) is False:
                        print("Error: {}".format(new_api_doc))
                        continue
                    else:
                        _meta['timestamp'] = datetime.now().isoformat()
                        new_api_doc['_meta'] = _meta
                        status = self.save_api(
                            new_api_doc, override_owner=True, overwrite=True, dryrun=False, save_v2=True)
                        print("Success: {}".format(status))
                else:
                    print("Error: {}".format(new_api_doc))
            else:
                print("Doc {} unchanged".format(api_doc['_id']))
