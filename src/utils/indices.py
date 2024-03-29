import json
import os.path

from elasticsearch_dsl import Index

from model import SmartAPIDoc


def exists(model_class=SmartAPIDoc):
    return Index(model_class.Index.name).exists()


def setup(model_class=SmartAPIDoc):
    """
    Setup Elasticsearch Index with dynamic template.
    Run it on an open index to update dynamic mapping.
    """

    if not exists(model_class):
        model_class.init()

    if model_class == SmartAPIDoc:
        # set up custom mapping for SmartAPI index
        _dirname = os.path.dirname(__file__)
        with open(os.path.join(_dirname, "mapping.json"), "r") as file:
            mapping = json.load(file)
        Index(model_class.Index.name).put_mapping(body=mapping)


def delete(model_class=SmartAPIDoc):
    Index(model_class.Index.name).delete()


def reset(model_class=SmartAPIDoc):
    if exists(model_class):
        delete(model_class)

    setup(model_class)


def refresh(model_class=SmartAPIDoc):
    index = Index(model_class.Index.name)
    index.refresh()
