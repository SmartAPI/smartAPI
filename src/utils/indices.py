from elasticsearch_dsl import Index
from model import SmartAPIDoc


def exists(model_class=SmartAPIDoc, index=None):
    return Index(index or model_class.Index.name).exists()


def setup(model_class=SmartAPIDoc, index=None):
    """
    Setup Elasticsearch Index with dynamic template.
    Run it on an open index to update dynamic mapping.
    """

    if not exists(model_class, index=index):
        model_class.init(index=index)

    # if model_class == SmartAPIDoc:
    #     # set up custom mapping for SmartAPI index
    #     _dirname = os.path.dirname(__file__)
    #     with open(os.path.join(_dirname, "mapping.json"), "r") as file:
    #         mapping = json.load(file)
    #     Index(model_class.Index.name).put_mapping(body=mapping)


def delete(model_class=SmartAPIDoc, index=None):
    Index(index or model_class.Index.name).delete()


def reset(model_class=SmartAPIDoc, index=None):
    if exists(model_class, index=index):
        delete(model_class, index=index)

    setup(model_class, index=index)


def refresh(model_class=SmartAPIDoc, index=None):
    idx = Index(index or model_class.Index.name)
    idx.refresh()
