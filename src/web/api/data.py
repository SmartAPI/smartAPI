import json 
import boto3

from elasticsearch_dsl import Index, Search

from ..model.api_doc import API_Doc
from ..controllers.controller import SWAGGER2_INDEXED_ITEMS


class SmartAPIData():
    """
    This class provides methods to:
    -backup all docs to file or S3
    -restore docs from local file with v2 and v3 support
    -fetch all docs in current index
    """

    def __init__(self):
        self.index_name = API_Doc.Index.name

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

    @classmethod
    def backup_all(cls, outfile=None, aws_s3_bucket=None):
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
        doc_li = cls.fetch_all(as_list=True)
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

    @classmethod
    def restore_all_with_file(cls, backupfile, overwrite=False):
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
            if overwrite and ask("Warning: index \"{}\" exists. Do you want to overwrite it?".format(cls.index_name)) == 'Y':
                Index(index_name).delete()
            else:
                print("Error: index \"{}\" exists. Try a different index_name.".format(cls.index_name))
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