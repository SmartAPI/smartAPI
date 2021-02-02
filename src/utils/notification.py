"""
    API registration slack notification
"""
import requests

try:
    from config import SLACK_WEBHOOKS
except ImportError:
    SLACK_WEBHOOKS = []

class Message():
    """
    Notify of new API registered by user
    Processable fields: title, description, _id
    """

    def __init__(self, user, api):
        self.user = user
        self.api = api
        self.translator_api = self.api.get('x-translator', False)

    def to_slack_payload(self):
        """
        Generate slack webhook notification payload.
        https://api.slack.com/messaging/composing/layouts
        """
        blocks = []

        if self.translator_api:
            header_title = ":large_purple_circle: New Translator API Registered"
            color = "#642F6B"
        else:
            header_title = ":large_blue_circle: New API Registered"
            color = "#3080C1"

        blocks.append({
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": header_title,
                    "emoji": True
                }
            })
        blocks.append({
            "type": "divider"
        })

        if self.api.get('info', {}).get('title', ''):
            blocks.append({
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "*Name*: " + self.api['info']['title']
			}
		})

        if self.api.get('info', {}).get('description', ''):
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Description*: " + self.api['info']['description']
                }
            })

        if self.user:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Registered by*: <https://github.com/{self.user}|{self.user}>"
                }
            })

        if self.api.get('_id', ''):
            registry_url = f"http://smart-api.info/registry?q={self.api['_id']}"
            docs_url = f"http://smart-api.info/ui/{self.api['_id']}"

            blocks.append({
			"type": "context",
			"elements": [
				{
					"type": "image",
					"image_url": "https://smart-api.info/static/img/owl-fly.gif",
					"alt_text": "SmartAPI"
				},
				{
					"type": "mrkdwn",
					"text": f"<{registry_url}|View on SmartAPI>"
				},
				{
					"type": "plain_text",
					"text": "   |  "
				},
				{
					"type": "mrkdwn",
					"text": ":book:"
				},
				{
					"type": "mrkdwn",
					"text": f"<{docs_url}|View API Documentation>"
				}
			]
		})

        return {
            "attachments": [{
                "color": color,
                "blocks": blocks
            }]
        }
    
    def send(self):
        for web_hook in SLACK_WEBHOOKS:
            # do not post on translator channel until approved
            if not 'translator' in web_hook['tags']:
                print(web_hook['url'])
                return requests.post(web_hook['url'], json=self.to_slack_payload())


# -------------
#    Tests
# -------------

# basic api
slack_msg = Notification({
    "_id": "8f08d1446e0bb9c2b323713ce83e2bd3",
    "openapi": "3.0.0",
    "info": {
        "contact": {
            "email": "help@biothings.io",
            "name": "Chunlei Wu",
            "x-id": "https://github.com/newgene",
            "x-role": "responsible developer"
        },
        "description": "This is just a test :)  Learn more about [MyChem.info](http://MyChem.info/)",
        "termsOfService": "http://MyChem.info/terms",
        "title": "[TEST] My API Title",
        "version": "1.0"
    }
})


def test_slack():
    """test slack notification on main channel
    """
    response = slack_msg.send()
    print(response.status_code)

if __name__ == '__main__':
    test_slack()