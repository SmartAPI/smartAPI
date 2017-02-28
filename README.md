# smartAPI
Intelligent APIs for a more connected web.

A BD2K/Network-of-BioThings project.

smartAPI allows API publishers to annotate their services and input/output parameters in a structured and identifiable manner, based on a standard JSON-LD format for biomedical APIs and services. By indexing and visualizing these descriptions as Linked Data in a MongoDB back-end, researchers can seamlessly identify the services that consume or return desired parameters, and automatically compose services in workflows that yield new insights. 

Presentation: http://bit.ly/smartAPIslides 

Repo: https://github.com/WebsmartAPI/smartAPI

Roadmap: https://docs.google.com/document/d/1mEQs5NuOr23p8iMfNkF01Kxbf8iJz63SE43D9DSpG_o/edit?usp=sharing


# How to run a dev API server locally
 1. Install Elasticsearch at localhost:9200 (follow [this instruction](https://www.elastic.co/guide/en/elasticsearch/reference/current/_installation.html))
 2. Clone this repo
 3. Install python dependencies
 ```
 pip install -r src/requirements.txt
 ```

 4. ```cd src/api/```
 5. Create index and index some example API metadata in Python shell:
 ```
 import es
 es.create_index()
 es.index_swagger(swagger_doc)
 ```
 
   *swagger_doc* is the input example API metadata object in JSON format
   
 6. run dev server
 ```
 python index.py --debug
 ```
 
  You should now able to access API dev server at http://localhost:8000
