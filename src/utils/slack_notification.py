import json
import requests
from config import SLACK_WEBHOOKS
from tornado.httpclient import HTTPRequest, AsyncHTTPClient

def get_tags(data):
	"""Generate array of all the tags listed in the newly registered API"""
	tags = []
	if('tags' in data):
		for item in data['tags']:
			tags.append(item['name'])
	return tags

def generate_slack_params(data, res, user):
	"""Generate parameters that will be used in slack post request. 
	
	In this case, markdown is used to generate formatting that 
	will show in Slack message
	"""
	api_title = data["info"]["title"]
	api_description = data["info"]["description"]
	api_id = res["_id"]
	api_url =  "http://smart-api.info/registry?q=" + api_id
	block_markdown = ("A new API has been registered on SmartAPI.info:  \n\t*API Title:* " 
					+ api_title + "\n\t*API Description:* " + api_description + "\n\t*SmartAPI Registry URL:* " 
					+ api_url + "\n\t*By User:* " + user)
	params = {
        "attachments": [{
        	"color": "#b0e3f9",
            "blocks": [{
				"type": "section",
				"text": {
					"type": "mrkdwn",
					"text": block_markdown
				}
			}]
        }]
    }
	return params

def send_slack_msg(data, res, user):
	"""Make requests to slack to post information about newly registered API. 
	
	Notifications will be sent to every 
	channel/webhook that is not tag specific, or will be sent to
	slack if the registered API contains a tag that is also specific
	a channel/webhook. 
	"""
	headers = {'content-type': 'application/json'}
	data_tags = get_tags(data)
	params = generate_slack_params(data, res, user)
	http_client = AsyncHTTPClient()
	for x in SLACK_WEBHOOKS:
		if(x['tag_specific']):
			if(x['tag'] in data_tags):
				req = HTTPRequest(url=x['webhook'], method='POST', body=json.dumps(params), headers=headers)
				http_client = AsyncHTTPClient()
				http_client.fetch(req)
		else:
			req = HTTPRequest(url=x['webhook'], method='POST', body=json.dumps(params), headers=headers)
			http_client = AsyncHTTPClient()
			http_client.fetch(req)


# res = requests.post(x['webhook'], json.dumps(params), headers=headers)
# res.raise_for_status()


# http_client = AsyncHTTPClient()
# http_client.fetch(req)