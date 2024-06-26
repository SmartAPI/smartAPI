import json
import os.path

from elasticsearch_dsl import Index

from model import SmartAPIDoc


def exists(index_name=None, model_class=SmartAPIDoc):
    index_name = index_name or model_class.Index.name
    return Index(index_name).exists()

def delete(index_name):
    Index(index_name).delete()

def setup(index_name=None, model_class=SmartAPIDoc):
    index_name = index_name or model_class.Index.name
    if not exists(model_class):
        model_class.init(index_name)

    if model_class == SmartAPIDoc:
        # set up custom mapping for SmartAPI index
        _dirname = os.path.dirname(__file__)
        with open(os.path.join(_dirname, "mapping.json"), "r") as file:
            mapping = json.load(file)
        Index(index_name).put_mapping(body=mapping)

def reset(model_class=SmartAPIDoc, index_name=None):
    index_name = index_name or model_class.Index.name
    if exists(index_name, model_class):

        print("Deleting index: ", index_name)

        delete(index_name)

    setup(index_name, model_class)    


def refresh(model_class=SmartAPIDoc, index_name=None):
    # Use the provided index name if it's not None, otherwise use the default index name
    index_name = index_name or model_class.Index.name

    index = Index(index_name)
    index.refresh()
