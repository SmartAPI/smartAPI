import json
import requests
from config_key import SLACK_WEBHOOKS

def GetTags(data):
	'''
	Generate array of all the tags listed in the newly registered API
	'''
	tags = []
	if('tags' in data):
		for item in data['tags']:
			tags.append(item['name'])
	return tags

def GenerateSlackParams(data, res, user):
	'''
	Generate parameters that will be used in slack post request. 
	In this case, markdown is used to generate formatting that 
	will show in Slack message
	'''
	API_title = data["info"]["title"]
	API_Description = data["info"]["description"]
	API_id = res["_id"]
	API_URL =  "http://smart-api.info/registry?q=" + API_id
	block_markdown = "A new API has been registered on smartAPI.info:  \n\n\t *API Title:* " + API_title + "\n\n\t*API Description:* " + API_Description + "\n\n\t*SmartAPI Registry URL:* " + API_URL + "\n\n\t*By User:* " + user
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

def AddToSlack(data, res, user):
	'''
	Make requests to slack to post information about newly registered
	API. Notifications will be sent to every channel/webhook that is
	not tag specific, or will be sent to slack if the registered API
	contains a tag that is also specific a channel/webhook. 
	'''
	headers = {'content-type': 'application/json'}
	data_tags = GetTags(data)
	params = GenerateSlackParams(data, res, user)
	for x in SLACK_WEBHOOKS:
		if(x['tag_specific']):
			if(x['tag'] in data_tags):
				res = requests.post(x['webhook'], json.dumps(params), headers=headers)
				res.raise_for_status()
		else:
			res = requests.post(x['webhook'], json.dumps(params), headers=headers)
			res.raise_for_status()
