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
        title = self.api.get('info', {}).get('title', '')

        if self.translator_api:
            header_title = ":large_purple_circle: New Translator API Registered"
            fallback_text = f":large_purple_circle: New API Registered: {title}"
        else:
            header_title = ":large_blue_circle: New API Registered"
            fallback_text = f":large_blue_circle: New API Registered: {title}"

        blocks.append({
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": header_title,
                    "emoji": True
                }
            })

        description = self.api.get('info', {}).get('description', '')[:120] + '...'
        user = self.user

        blocks.append({
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": f"*Name*: {title} \n *Description*: {description} \n *Registered by*: <https://github.com/{user}|{user}>"
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
					"text": " | "
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
        # send as message
        return {
            "text": fallback_text,
            "blocks": blocks
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