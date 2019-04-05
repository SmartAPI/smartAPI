# SmartAPI
Intelligent APIs for a more connected web.

A BD2K/Network-of-BioThings project.

SmartAPI allows API publishers to annotate their services and input/output parameters in a structured and identifiable manner, based on a standard JSON-LD format for biomedical APIs and services. By indexing and visualizing these descriptions as Linked Data in a Elasticsearch back-end, researchers can seamlessly identify the services that consume or return desired parameters, and automatically compose services in workflows that yield new insights.

Presentation: http://bit.ly/smartAPIslides  
Contact: api-interoperability@googlegroups.com  


# How to run a dev API server locally
1. Install Elasticsearch at localhost:9200 (follow [this instruction](https://www.elastic.co/guide/en/elasticsearch/reference/current/_installation.html))
2. Clone this repo
    ```
    git clone https://github.com/SmartAPI/smartAPI.git
    ````
3. Install system packages (on Ubuntu, for example)
    ```
    sudo apt install libcurl4-openssl-dev libssl-dev aws-cli
    ```
4. Change directory to SmartAPI source files
    ```
    cd smartAPI/src
    ```
3. Install python dependencies
    ```
    pip install -r requirements.txt
    ```
5. Create a *config_key.py* under *src* with
    ```
    COOKIE_SECRET = '<Any Random String>'
    GITHUB_CLIENT_ID = '<your Github application Client ID>'
    GITHUB_CLIENT_SECRET = '<your Github application Client Secret>'
    ```
    Follow [this instruction](https://developer.github.com/apps/building-oauth-apps/creating-an-oauth-app/) to create your Github Client ID and Secret.   
    Enter any _Application name_, `http://localhost:8000/` for _Homepage 
    URL_ and `http://localhost:8000/oauth` for _Authorization callback URL_.
6. Create index in Python shell:
    ```
    from api import es  
    es.create_index()
    ```
   Or import some API data from a saved dump file. Contact us for the dump file.  
   And replace the name of the file in the command with the backup file name.
    ```
    from api import es
    esq = es.ESQuery()
    esq.restore_all("smartapi_oas3_backup_20190128.json", es.ES_INDEX_NAME)
    ```
8. Run dev server
    ```
    python index.py --debug
    ```
You should now able to access API dev server at http://localhost:8000
