# SmartAPI
Intelligent APIs for a more connected web.

A BD2K/Network-of-BioThings project.

SmartAPI allows API publishers to annotate their services and input/output parameters in a structured and identifiable manner, based on a standard JSON-LD format for biomedical APIs and services. By indexing and visualizing these descriptions as Linked Data in a Elasticsearch back-end, researchers can seamlessly identify the services that consume or return desired parameters, and automatically compose services in workflows that yield new insights.

Presentation: http://bit.ly/smartAPIslides  
Contact: api-interoperability@googlegroups.com  


# How to run a dev API server locally
1. Install Elasticsearch (version 6.x) at localhost:9200 (follow [this instruction](https://www.elastic.co/downloads/elasticsearch)) or install with docker (follow [this instruction](https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html))
2. Clone this repo
    ```
    git clone https://github.com/SmartAPI/smartAPI.git
    ````
3. Install system packages (on Ubuntu, for example)
    ```
    sudo apt install libcurl4-openssl-dev libssl-dev aws-cli
    ```
4. Install python dependencies after navigating to root smartAPI directory
    ```
    cd smartAPI
    pip install -r requirements.txt
    ```
5. Navigate to SmartAPI source files and create a *config_key.py* under *src*
    ```
    cd src
    touch config_key.py
    ```
6. Update *config_key.py* with
    ```
    COOKIE_SECRET = '<Any Random String>'
    GITHUB_CLIENT_ID = '<your Github application Client ID>'
    GITHUB_CLIENT_SECRET = '<your Github application Client Secret>'
    SLACK_WEBHOOKS = [
	    {
		    "tag_specific": <Boolean>, 
		    "tag": <string if tag_specific is True> <None if tag_specific is False>,
		    "webhook": <insert webhook URL> 
	    }
    ]
    ```
    For Github incorporation, follow [this instruction](https://developer.github.com/apps/building-oauth-apps/creating-an-oauth-app/) to create your Github Client ID and Secret.   
    Enter any _Application name_, `http://localhost:8000/` for _Homepage 
    URL_ and `http://localhost:8000/oauth` for _Authorization callback URL_.
    
    For SLACK_WEBHOOKS (optional), the list may be left empty if one does not want Slack notifications pushed every time a new API is added to the smartAPI registry, such that: 
    ```
    SLACK_WEBHOOKS = []
    ```
    Alternatively, if one wants slack notifications sent to more than one channel, one may list more than one dict in the ```SLACK_WEBHOOKS``` list.
    
    Follow [this instruction](https://slack.com/help/articles/115005265063-Incoming-Webhooks-for-Slack) to create Slack webhooks and obtain webhook URLs. 
    
    Finally, if one would like a Slack notification pushed if the newly registered API contains a specific tag, one should set ```tag_specific``` to ```True```, and the ```tag``` key should have the value of the specific tag (case sensitive). 
    
7. Create index in Python (version 3.x) shell:
    ```
    from api import es  
    es.create_index()
    ```
   Or import some API data from a saved dump file. Contact us for the dump file.  
   And replace the name of the file in the command with the backup file name.
    ```
    from web.api import es
    esq = es.ESQuery()
    esq.restore_all("smartapi_oas3_backup_20200706.json", es.ES_INDEX_NAME)
    ```
8. Run dev server
    ```
    python index.py --debug
    ```
You should now able to access API dev server at http://localhost:8000
