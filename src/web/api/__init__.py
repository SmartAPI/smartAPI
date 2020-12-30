'''
    Elasticsearch Document Object Model
    - The ES backend is a collection of these documents
    - API_Doc
    Reference: https://schema.org/docs/datamodel.html
'''
import os

from elasticsearch_dsl import connections

from .model import APIDoc

__all__ = [
    'APIDoc'
]

# parse environment variables
ES_HOST = os.getenv('ES_HOST', 'localhost:9200')

# create a default connection
connections.create_connection(hosts=ES_HOST)
