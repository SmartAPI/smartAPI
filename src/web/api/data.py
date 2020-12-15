import json 
import boto3
import logging

from elasticsearch_dsl import Index, Search

from .model import API_Doc
from .controller import SWAGGER2_INDEXED_ITEMS, APIDocController, polite_requests, get_api_metadata_by_url, APIRequestError


class SmartAPIData():
    """
    This class provides methods to:
    
    -backup all docs to file or S3
    -restore docs from local file with v2 and v3 support
    -refresh one doc
    -refresh all docs from list

    -fetch all docs in current index
    """

    def __init__(self):
        self.index_name = API_Doc.Index.name

    def _refresh_one(self, api_doc, user=None, override_owner=False, dryrun=True,
                     error_on_identical=False, save_v2=False):
        ''' refresh the given API document object based on its saved metadata url  '''
        _id = api_doc['_id']
        _meta = api_doc['_meta']

        res = get_api_metadata_by_url(_meta['url'])
        if res and isinstance(res, dict):
            if not res:
                res['error'] = '[Request] '+res.get('error', '')
                status = res
            else:
                _meta['timestamp'] = datetime.now().isoformat()
                res['_meta'] = _meta

                _id = res["_id"]

                try:
                    doc = APIDocController(_id=_id)
                    status = doc.refresh_api(_id=_id, user=user, test=False)
                except APIRequestError as err:
                    status = str(err)

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

    def fetch_all(self, as_list=False, id_list=[], query={}):
        """return a generator of all docs from the ES index.
            return a list instead if as_list is True.
            if query is passed, it returns docs that match the query.
            else if id_list is passed, it returns only docs from the given ids.
        """
        if query:
            _query = query
        elif id_list:
            _query = {"query": {"ids": {"values": id_list}}}
        else:
            _query = {"query": {"match_all": {}}}

        scan_res = Search(index=self.index_name).scan(query=_query)

        def _fn(x):
            x['_source'].setdefault('_id', x['_id'])
            return x['_source']

        doc_iter = (_fn(x) for x in scan_res)    # return docs only
        if as_list:
            return list(doc_iter)
        else:
            return doc_iter

    def backup_all(self, outfile=None, aws_s3_bucket=None):
        """
        back up all docs to S3 or output file
        """
        # get the real index name in case index is an alias
        logging.info("Backup started.")
        alias_d = Index(cls.index_name).get_alias()
        assert len(alias_d) == 1
        index_name = list(alias_d.keys())[0]
        default_name = "{}_backup_{}.json".format(index_name, get_datestamp())
        outfile = outfile or default_name
        doc_li = self.fetch_all(as_list=True)
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

    def restore_all_with_file(self, backupfile, overwrite=False):
        """
        Delete existing index and restore all documents from local file. 

        Args:
            backupfile (file path): path to ES backup file
            overwrite (bool, optional): Overwrite entire index. Defaults to False.
        """

        def legacy_backupfile_support_path_str(_doc):
            """
            transform multiple key field 'paths' for swagger specification
            Args:
                _doc: raw doc
            Returns:
                transformed _doc: 'paths' field transformed for ES performance
            """
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
            """
            Maintain legacy structure for swagger specification
            """
            _d = {"_meta": _doc['_meta']}
            for key in SWAGGER2_INDEXED_ITEMS:
                if key in _doc:
                    _d[key] = _doc[key]
            _d['~raw'] = _doc['~raw']
            return _d
        
        if Index(cls.index_name).exists():
            if overwrite and ask("Warning: index \"{}\" exists. Do you want to overwrite it?".format(self.index_name)) == 'Y':
                Index(index_name).delete()
            else:
                print("Error: index \"{}\" exists. Try a different index_name.".format(self.index_name))
                return

        print("Loading docs from \"{}\"...".format(backupfile), end=" ")
        in_f = open(backupfile)
        doc_li = json.load(in_f)
        print("Done. [{} Documents]".format(len(doc_li)))

        print("Creating index...", end=" ")
        API_Doc.init()
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
            # self._es.index(index=index_name,
            #                doc_type=self._doc_type, body=_doc, id=_id)
            doc = API_Doc(meta={'id': _id}, ** _doc)
            doc.save()
        print(swagger_v2_count, ' Swagger Objects and ',
              openapi_v3_count, ' Openapi Objects. ')
        print("Done.")