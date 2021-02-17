

import json
import logging
from datetime import datetime

import boto3

from controller import SmartAPI
from utils import indices

logging.basicConfig(level="INFO")


def _default_filename():
    return "smartapi_" + datetime.today().strftime("%Y%m%d") + ".json"


def save_to_file(mapping, filename=None):
    filename = filename or _default_filename()
    with open(filename, 'w') as file:
        json.dump(mapping, file, indent=2)


def save_to_s3(mapping, filename=None, bucket="smartapi"):
    filename = filename or _default_filename()
    s3 = boto3.resource('s3')
    s3.Bucket(bucket).put_object(
        Key='db_backup/{}'.format(filename),
        Body=json.dumps(mapping, indent=2)
    )


def _backup():
    smartapis = []
    for smartapi in SmartAPI.get_all(1000):
        smartapis.append({
            "url": smartapi.url,
            "username": smartapi.username,
            "slug": smartapi.slug,
            "date_created": smartapi.date_created.isoformat(),
            "last_updated": smartapi.last_updated.isoformat(),
            "raw": smartapi.raw.decode()  # to string
        })
    return smartapis


def backup_to_file(filename=None):
    smartapis = _backup()
    save_to_file(smartapis, filename)


def backup_to_s3(filename=None, bucket="smartapi"):
    smartapis = _backup()
    save_to_s3(smartapis, filename, bucket)


backup = backup_to_file


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


def restore_from_s3(filename, bucket="smartapi"):
    s3 = boto3.resource('s3')
    obj = s3.get_object(
        Bucket=bucket,
        Key='db_backup/{}'.format(filename)
    )
    smartapis = json.loads(obj)
    _restore(smartapis)


def restore_from_file(filename):
    with open(filename) as file:
        smartapis = json.load(file)
        _restore(smartapis)


restore = restore_from_file


def refresh():
    for smartapi in SmartAPI.get_all(1000):
        logging.info(smartapi._id)
        smartapi.refresh()
        smartapi.save()


def check():
    for smartapi in SmartAPI.get_all(1000):
        logging.info(smartapi._id)
        smartapi.check()
        smartapi.save()


def routine():
    refresh()
    check()
