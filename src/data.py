import json
import boto3
import logging
from datetime import datetime, date
import requests

from elasticsearch_dsl import Index, Search

from model import APIDoc
from controller import SWAGGER2_INDEXED_ITEMS, APIDocController, Downloader, RegistryError
from utils.indices import setup_data

def get_datestamp():
    d = date.today()
    return d.strftime('%Y%m%d')

def ask(prompt, options='YN'):
    '''
    Prompt Yes or No,return the upper case 'Y' or 'N'
    '''
    options = options.upper()
    while 1:
        s = input(prompt+'[%s]' % '|'.join(list(options))).strip().upper()
        if s in options:
            break
    return s

class SmartAPIData():
    """
    Backup docs to S3 and refresh docs based on registered url
    """

    def __init__(self):
        self.index_name = APIDoc.Index.name

    @staticmethod
    def polite_requests(url, head=False):
        try:
            if head:
                res = requests.head(url, timeout=5)
            else:
                res = requests.get(url, timeout=5)
        except requests.exceptions.Timeout:
            return False
        except requests.exceptions.ConnectionError:
            return False
        except requests.exceptions.RequestException:
            return False
        if res.status_code != 200:
            return False
        return res

    def _refresh_one(self, api_doc):

        '''
        refresh the given API document object based on its saved metadata url
        '''
        _id = api_doc['_id']
        _meta = api_doc['_meta']

        res = Downloader.get_api_metadata_by_url(_meta['url'])

        _meta['timestamp'] = datetime.now().isoformat()
        res['_meta'] = _meta

        try:
            doc = APIDocController.from_dict(res)
            status = doc.refresh_api(_id)
        except RegistryError as err:
            status = str(err)

        return status

    def refresh_all(self, id_list=[], use_etag=True):
        '''
        refresh saved API documents based on their metadata urls.

        :param id_list: the list of API documents to perform the refresh operation
        :param use_etag: by default, HTTP ETag is used to speed up version detection
        '''
        updates = 0
        status_li = []
        logging.info("Refreshing API metadata:")

        for api_doc in self.fetch_all(id_list=id_list):

            _id, status = api_doc['_id'], ''

            if use_etag:
                url = api_doc.get('_meta', {}).get('url', '')
                _res = self.polite_requests(url, head=True)
                if _res:
                    etag_local = api_doc.get('_meta', {}).get('ETag', '')
                    etag_server = _res.headers.get('ETag', 'N').strip('W/"')
                    if etag_local == etag_server:
                        status = f"No changes ID {_id} (Via Etag)"

            if not status:
                try:
                    res = self._refresh_one(api_doc)
                except RegistryError as err:
                    status = err
                else:
                    # status is f"API with ID {_id} was refreshed"
                    status = res
                    updates += 1

            status_li.append((_id, status))
            logging.info(f"Updated {_id}: {status}")

        logging.info("%s: %s APIs refreshed. %s Updates.", get_datestamp(), len(status_li), updates)

        return status_li

    def fetch_all(self, as_list=False, id_list=[], query={}):
        """
        return a generator of all docs from the ES index.
        return a list instead if as_list is True.
        if query is passed, it returns docs that match the query.
        else if id_list is passed, it returns only docs from the given ids.
        """
        search = Search(index=self.index_name)

        if query:
            search = search.from_dict(query)
        elif id_list:
            search = search.from_dict({"query": {"ids": {"values": id_list}}})

        scan_res = search.scan()

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
        alias_d = Index(self.index_name).get_alias()
        assert len(alias_d) == 1

        index_name = list(alias_d.keys())[0]
        default_name = "{}_backup_{}.json".format(index_name, get_datestamp())
        outfile = outfile or default_name
        doc_li = self.fetch_all(as_list=True)

        if aws_s3_bucket:
            location_prompt = 'on S3'
            s3 = boto3.resource('s3')
            s3.Bucket(aws_s3_bucket).put_object(
                Key='db_backup/{}'.format(outfile),
                Body=json.dumps(doc_li, indent=2))
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
            overwrite (bool, required): Overwrite entire index. Must be true to proceed.
        """

        def legacy_backupfile_support_path_str(_doc):
            """
            'paths' field transformed for ES performance
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

        logging.info("Restore from file started")
        if Index(self.index_name).exists():
            if overwrite:
                logging.info(f"Index {self.index_name} deleted")
                Index(self.index_name).delete()
            else:
                logging.info("Restore from file aborted.  set 'override' to True to retry.")
                raise RegistryError("Error: index \"{}\" exists. Try a different index_name.".format(self.index_name))

        in_f = open(backupfile)
        doc_li = json.load(in_f)

        setup_data()
        logging.info(f"Index {self.index_name} created")

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
            doc = APIDoc(meta={'id': _id}, ** _doc)
            doc.save()

        logging.info(f"Openapi Objects {openapi_v3_count} indexed")
        logging.info(f"Swagger Objects {swagger_v2_count} indexed")
        logging.info("Restore from file complete")
