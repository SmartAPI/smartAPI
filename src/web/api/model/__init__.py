'''
    Elasticsearch Document Object Model
    - The ES backend is a collection of these documents
    - API Specification Docs
    Reference: https://schema.org/docs/datamodel.html
'''
import os

from elasticsearch_dsl import connections

from .api_doc import API_Doc

# list of docs to be initialized and exported
__all__ = [
    'API_Doc'
]

# parse environment variables
ES_HOST = os.getenv('ES_HOST', 'localhost:9200')

# create a default connection
connections.create_connection(hosts=ES_HOST)