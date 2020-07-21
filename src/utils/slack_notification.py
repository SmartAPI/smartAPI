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
	return re.sub('\[(?P<label>[^\[\]]+)\]\((?P<url>[^()]+)\)', '<\g<url>|\g<label>>', description)

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
	api_data = {
		"api_title": api_title, 
		"api_description": api_description,
		"registry_url": registry_url,
		"docs_url": docs_url,
		"github_user": github_user
	}
	# default markdown
	default_block_markdown_template = ("A new API has been registered on SmartAPI.info:\n\n"
						"*Title:* {api_title}\n"
						"*Description:* {api_description}\n"
						"*Registered By:* <https://github.com/{github_user}|{github_user}>\n\n"
						"<{registry_url}|View on SmartAPI Registry>  -  <{docs_url}|View API Documentation>")
	# get template - use default if one not provided
	block_markdown_tpl = webhook_dict.get("template", default_block_markdown_template)
	# fill template with variable values
	block_markdown = block_markdown_tpl.format(**api_data)
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