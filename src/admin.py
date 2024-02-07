"""
    Data Administration Module

    import admin

    admin.backup_to_file() # backup to cwd with the an auto-generated filename.
    admin.backup_to_s3() # backup to s3 with the an auto-generated filename.

    admin.restore_from_file(filename) # restore a backup file
    admin.restore_from_s3() # restore the latest s3 version

    # file operation shortcut
    admin.backup()
    admin.restore(filename)

    # update all documents
    admin.refresh()
    # check all uptime status
    admin.check()

    See below for additional usage.

"""

import json
import logging
from datetime import datetime

import boto3
from filelock import FileLock, Timeout

from controller import SmartAPI
from model import ConsolidatedMetaKGDoc, MetaKGDoc
from utils import indices

logging.basicConfig(level="INFO")


def _default_filename():
    return "smartapi_" + datetime.today().strftime("%Y%m%d") + ".json"


def save_to_file(mapping, filename=None):
    filename = filename or _default_filename()
    with open(filename, "w") as file:
        json.dump(mapping, file, indent=2)


def save_to_s3(mapping, filename=None, bucket="smartapi"):
    filename = filename or _default_filename()
    s3 = boto3.resource("s3")
    s3.Bucket(bucket).put_object(Key="db_backup/{}".format(filename), Body=json.dumps(mapping, indent=2))


def _backup():
    smartapis = []
    for smartapi in SmartAPI.get_all(1000):
        smartapis.append(
            {
                "url": smartapi.url,
                "username": smartapi.username,
                "slug": smartapi.slug,
                "date_created": smartapi.date_created.isoformat(),
                "last_updated": smartapi.last_updated.isoformat(),
                "raw": smartapi.raw.decode(),  # to string
                "has_metakg": smartapi.has_metakg
            }
        )
    return smartapis


def backup_to_file(filename=None):
    smartapis = _backup()
    save_to_file(smartapis, filename)


def backup_to_s3(filename=None, bucket="smartapi"):
    smartapis = _backup()
    save_to_s3(smartapis, filename, bucket)


def _restore(smartapis):
    if indices.exists():
        logging.error("Cannot write to an existing index.")
        return
    indices.reset()
    for smartapi in smartapis:
        logging.info(smartapi["url"])
        _smartapi = SmartAPI(smartapi["url"])
        _smartapi.username = smartapi["username"]
        _smartapi.slug = smartapi["slug"]
        _smartapi.date_created = datetime.fromisoformat(smartapi["date_created"])
        _smartapi.last_updated = datetime.fromisoformat(smartapi["last_updated"])
        _smartapi.raw = smartapi["raw"].encode()  # to bytes
        _smartapi.save()


def restore_from_s3(filename=None, bucket="smartapi"):
    s3 = boto3.client("s3")

    if not filename:
        objects = s3.list_objects_v2(Bucket="smartapi", Prefix="db_backup")["Contents"]
        filename = max(objects, key=lambda x: x["LastModified"])["Key"]

    if not filename.startswith("db_backup/"):
        filename = "db_backup/" + filename

    logging.info("GET s3://%s/%s", bucket, filename)

    obj = s3.get_object(Bucket=bucket, Key=filename)
    smartapis = json.loads(obj["Body"].read())
    _restore(smartapis)


def restore_from_file(filename):
    with open(filename) as file:
        smartapis = json.load(file)
        _restore(smartapis)


def refresh_document():
    logger = logging.getLogger("refresh")
    for smartapi in SmartAPI.get_all(1000):
        logger.info(smartapi._id)
        _status = smartapi.refresh()
        logger.info(_status)
        try:
            smartapi.save()
        except Exception as e:
            logger.error("%s: %s", smartapi._id, repr(e))


def check_uptime():
    logger = logging.getLogger("uptime")
    for smartapi in SmartAPI.get_all(1000):
        logger.info("Checking API: %s", smartapi._id)
        _status = smartapi.check()
        logger.debug(_status)
        logger.info("Done")
        print("-" * 50)
        smartapi.save()


def debug_uptime(_id, endpoint=None):
    """
    Debug uptime status check for a given SmartAPI.
    If endpoint is provided, by path (e.g. "/taxon"), only check for that endpoint.
    """
    from utils import monitor

    logger = monitor.logger
    cur_level = logger.level
    logger.setLevel(logging.DEBUG)
    try:
        api = monitor.API(dict(SmartAPI.get(_id)))
        if endpoint:
            _endpoint_info = api.endpoints_info[endpoint]
            _status = api.test_endpoint(endpoint, _endpoint_info)
            logger.info("_status: %s", _status)
        else:
            api.check_api_status()
    finally:
        logger.setLevel(cur_level)


def resave():
    # when index mappings are changed
    logger = logging.getLogger("resave")
    for smartapi in SmartAPI.get_all(1000):
        logger.info(smartapi._id)
        smartapi.save()


def refresh_metakg(reset=True, include_trapi=True):
    es_logger = logging.getLogger("elasticsearch")
    es_logger.setLevel("WARNING")

    if reset:
        logging.info("Reset MetaKG index")
        indices.reset(MetaKGDoc)

    logging.info("Refreshing MetaKG index")
    SmartAPI.refresh_metakg(include_trapi=include_trapi)


def consolidate_metakg(reset=True):
    """Consolidate the MetaKG edge data into documents based on a subject-predicate-object key.
    Creates an index with the groups.
    *** Currently, must be run after running refresh_metakg()
    """
    if reset:
        logging.info("Reset ConsolidatedMetaKG index")
        indices.reset(ConsolidatedMetaKGDoc)

    logging.info("Consolidating/Refreshing MetaKG edges")
    SmartAPI.index_metakg_consolidation()


restore = restore_from_file
backup = backup_to_file

refresh = refresh_document
check = check_uptime

# only one process should perform backup routines
_lock = FileLock(".lock", timeout=0)
try:  # it will be released upon exit
    _lock.acquire()
except Timeout:
    pass


def routine():
    logger = logging.getLogger("routine")

    try:
        # if previously acquired,
        # it won't block here
        _lock.acquire()
    except Timeout:
        logger.warning("Skips routine, it's already running in another process.")
        return
    logger.info("backup_to_s3()")
    backup_to_s3()
    logger.info("refresh_document()")
    refresh_document()
    logger.info("check_uptime()")
    check_uptime()
    logger.info("refresh_metakg()")
    refresh_metakg()
    logger.info("consolidate_metakg()")
    consolidate_metakg()


if __name__ == "__main__":
    restore_from_s3()
