import json
import requests
import re
from tornado.httpclient import HTTPRequest, AsyncHTTPClient

try:
	from config import SLACK_WEBHOOKS
except ImportError: 
	SLACK_WEBHOOKS = []

def get_tags(data):
	"""Generate array of all the tags listed in the newly registered API"""
	tags = []
	if('tags' in data):
		for item in data['tags']:
			tags.append(item['name'])
	return tags

def change_link_markdown(description):
	"""Change markdown styling of links to match fit Slack Markdown styling
	
	Description text links formatted as [link name](URL), we want <URL|link name>
	"""
	description = description.split(" ")
	# check each word in string
	for i in range(len(description)): 
		if((description[i][0] == '[') and (description[i][-1] == ")") and ("](" in description[i])):
			description[i] = description[i].replace("[","").replace(")","")
			temp_list = description[i].split("](")
			description[i] = "<" + temp_list[1] + "|" + temp_list[0] + ">"
	return " ".join(str(x) for x in description)

def generate_slack_params(data, res, github_user, webhook_dict):
	"""Generate parameters that will be used in slack post request. 
	
	In this case, markdown is used to generate formatting that 
	will show in Slack message
	"""
	api_title = data["info"]["title"]
	# limit API description to 120 characters
	api_description = ((data["info"]["description"][:120] + '...') 
						if len(data["info"]["description"]) > 120 
						else data["info"]["description"])
	api_description = change_link_markdown(api_description)
	api_id = res["_id"]
	registry_url =  f"http://smart-api.info/registry?q={api_id}" 
	docs_url = f"http://smart-api.info/ui/{api_id}"
	if("template" in webhook_dict):
		# update custom template with actual variables. Unable to use inline updates
		# for fixed template set as string
		block_markdown = (webhook_dict['template']
						.replace("{ ","")
						.replace(" }","")
						.replace("{","")
						.replace("}","")
						.replace("api_title", api_title)
						.replace("api_description", api_description)
						.replace("registry_url", registry_url)
						.replace("docs_url", docs_url)
						.replace("github_user", github_user)
						)
	else:
		# default markdown
		block_markdown = (f"A new API has been registered on SmartAPI.info:\n\n"
						f"	*Title:* {api_title}\n"
						f"	*Description:* {api_description}\n"
						f"	*Registered By:* <https://github.com/{github_user}|{github_user}>\n\n"
						f"	<{registry_url}|View on SmartAPI Registry>  -  <{docs_url}|View API Documentation>"
						)
	# Assemble params to be sent to slack 
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

def send_slack_msg(data, res, github_user):
	"""Make requests to slack to post information about newly registered API. 
	
	Notifications will be sent to every 
	channel/webhook that is not tag specific, or will be sent to
	slack if the registered API contains a tag that is also specific
	a channel/webhook. 
	"""
	headers = {'content-type': 'application/json'}
	data_tags = get_tags(data)
	http_client = AsyncHTTPClient()
	for x in SLACK_WEBHOOKS:
		send_request = False
		if('tags' in x):
			if(isinstance(x['tags'], str)):
				if(x['tags'] in data_tags):
					send_request = True
			elif(isinstance(x['tags'], list)):
				if(bool(set(x['tags']) & set(data_tags))):
					send_request = True
		else:
			send_request = True
		if(send_request):
			params = generate_slack_params(data, res, github_user, x)
			req = HTTPRequest(url=x['webhook'], method='POST', body=json.dumps(params), headers=headers)
			http_client = AsyncHTTPClient()
			http_client.fetch(req)