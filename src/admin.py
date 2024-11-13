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
import random
import time
import zipfile
import io
from datetime import datetime

import boto3
from controller import SmartAPI
from filelock import FileLock, Timeout
from model import ConsolidatedMetaKGDoc, MetaKGDoc
from utils import indices


def _default_filename(extension=".json"):
    return "smartapi_" + datetime.today().strftime("%Y%m%d") + extension


def save_to_file(mapping, filename=None, format="zip"):
    """
    Save data to a file in either JSON or ZIP format.
    :param mapping: Data to save
    :param filename: File name
    :param format: File format, either 'json' or 'zip'
    """
    if format == "zip":
        filename = filename or _default_filename(".zip")
        with zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED) as zfile:
            json_data = json.dumps(mapping, indent=2)
            zfile.writestr(filename.replace(".zip", ".json"), json_data)
    else:
        filename = filename or _default_filename(".json")
        with open(filename, "w") as file:
            json.dump(mapping, file, indent=2)


def save_to_s3(data, filename=None, bucket="smartapi", format="zip"):
    """
    Save data to S3 in either JSON or ZIP format.
    :param data: Data to save
    :param filename: File name
    :param bucket: S3 bucket name
    :param format: File format, either 'json' or 'zip'
    """
    filename = filename or _default_filename(f".{format}")
    s3 = boto3.resource("s3")

    if format == "zip":
        with zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED) as zfile:
            json_data = json.dumps(data, indent=2)
            zfile.writestr(filename.replace(".zip", ".json"), json_data)
        logging.info(f"Uploading {filename} to AWS S3")
        s3.Bucket(bucket).upload_file(Filename=filename, Key=f"db_backup/{filename}")
    else:
        logging.info(f"Uploading {filename} to AWS S3")
        s3.Bucket(bucket).put_object(Key=f"db_backup/{filename}", Body=json.dumps(data, indent=2))


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
            }
        )
    return smartapis


def backup_to_file(filename=None, format="zip"):
    smartapis = _backup()
    save_to_file(smartapis, filename, format)


def backup_to_s3(filename=None, bucket="smartapi", format="zip"):
    smartapis = _backup()
    save_to_s3(smartapis, filename, bucket, format)


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
        objects = s3.list_objects_v2(Bucket=bucket, Prefix="db_backup")["Contents"]
        filename = max(objects, key=lambda x: x["LastModified"])["Key"]

    if not filename.startswith("db_backup/"):
        filename = "db_backup/" + filename

    logging.info("GET s3://%s/%s", bucket, filename)

    obj = s3.get_object(Bucket=bucket, Key=filename)

    filename = filename.replace("db_backup/", "")

    if filename.endswith(".zip"):
        file_content = obj["Body"].read()
        with zipfile.ZipFile(io.BytesIO(file_content)) as zfile:
            # Search for a JSON file inside the ZIP
            json_file = next((f for f in zfile.namelist() if f.endswith(".json")), None)
            if not json_file:
                raise ValueError("No JSON file found inside the ZIP archive.")
            with zfile.open(json_file) as json_data:
                smartapis = json.load(json_data)
    elif filename.endswith(".json"):
        smartapis = json.loads(obj["Body"].read())
    else:
        raise Exception("Unsupported backup file type!")

    _restore(smartapis)


def restore_from_file(filename):
    if filename.endswith(".zip"):
        with zipfile.ZipFile(filename, 'r') as zfile:
            # Search for a JSON file inside the ZIP
            json_file = next((f for f in zfile.namelist() if f.endswith(".json")), None)
            if not json_file:
                raise ValueError("No JSON file found inside the ZIP archive.")
            with zfile.open(json_file) as json_data:
                smartapis = json.load(json_data)
    elif filename.endswith(".json"):
        with open(filename) as file:
            smartapis = json.load(file)
    else:
        raise Exception("Unsupported backup file type!")

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


def refresh_has_metakg():
    """
    Refreshes the 'has_metakg' attribute for SmartAPI objects.
    This function iterates through all SmartAPI objects, checks if there's a corresponding entry in the ConsolidatedMetaKGDoc
    collection based on the SmartAPI ID, and updates the 'has_metakg' attribute accordingly.
    Note:
    - This function assumes the existence of the SmartAPI and ConsolidatedMetaKGDoc classes.
    - 'has_metakg' attribute is a boolean value indicating whether a SmartAPI has corresponding metadata in the Meta-Knowledge Graph.
    Returns:
    None
    """
    for smartapi in SmartAPI.get_all(1000):
        value = ConsolidatedMetaKGDoc.exists(smartapi._id, field="api.smartapi.id")
        if value:
            smartapi.has_metakg = True
        else:
            smartapi.has_metakg = False
        smartapi.save()


restore = restore_from_file
backup = backup_to_file

refresh = refresh_document
check = check_uptime

# only one process should perform backup routines
_lock = FileLock(".lock", timeout=0)


def routine(no_backup=False, format="zip"):
    logger = logging.getLogger("routine")

    # Add jitter: random delay between 100 and 500 milliseconds (adjust range as needed)
    jitter_ms = random.uniform(100, 500)  # Jitter in milliseconds
    jitter_seconds = jitter_ms / 1000  # Convert milliseconds to seconds
    logger.info(f"Applying jitter delay of {jitter_ms:.2f} milliseconds before acquiring lock.")
    time.sleep(jitter_seconds)

    lock_acquired = False

    try:
        # if previously acquired,
        # it won't block here
        lock_acquired = _lock.acquire()
        if lock_acquired:
            logger.info("Schedule lock acquired successfully.")
            if not no_backup:
                logger.info(f"backup_to_s3(format={format})")
                backup_to_s3(format=format)
            logger.info("refresh_document()")
            refresh_document()
            logger.info("check_uptime()")
            check_uptime()
            logger.info("refresh_metakg()")
            refresh_metakg()
            logger.info("consolidate_metakg()")
            consolidate_metakg()
            logger.info("refresh_has_metakg()")
            refresh_has_metakg()
        else:
            logger.warning("Schedule lock acquired by another process. No need to run it in this process.")
    except Timeout:
        logger.warning("Schedule lock acquired by another process. No need to run it in this process.")
    except Exception as e:
        logger.error(f"An error occurred during the routine: {e}")
        logger.error("Stack trace:", exc_info=True)
    finally:
        if lock_acquired:
            _lock.release()
            logger.info("Schedule lock released successfully.")


if __name__ == "__main__":
    restore_from_s3()
