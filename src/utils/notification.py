"""
    API registration slack notification
"""
import requests

try:
    from config import SLACK_WEBHOOKS
except ImportError:
    SLACK_WEBHOOKS = []

class Notification(dict):
    """
    Processable fields: title, description, _id, x-translator
    """

    def __getattr__(self, attr):
        if attr in ('_id', 'title', 'description', 'x-translator'):
            if attr in self['title']:
                if attr == 'description':
                    return self['title'][attr][:150] + '...'
                return self['title'][attr]
            if attr in self:
                return self[attr]
            return ""
        raise AttributeError()

    def to_slack_payload(self):
        """
        Generate slack webhook notification payload.
        https://api.slack.com/messaging/composing/layouts
        """
        blocks = []
        blocks.append({
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": ":large_blue_circle: New API Registered",
                    "emoji": True
                }
            })
        blocks.append({
            "type": "divider"
        })

        if self.title:
            blocks.append({
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": ":large_blue_circle: " + self.title,
                    "emoji": True
                }
            })

        if self.description:
            body = {
                "type": "section",
                "text": {"type": "mrkdwn", "text": self.description},
            }
            blocks.append(body)

            if self['x-translator']:
                img_url = "https://smart-api.info/static/img/slack_translator.png"
            else:
                mg_url = "https://smart-api.info/static/img/owl-fly.gif"

            body["accessory"] = {
                "type": "image",
                "image_url": img_url,
                "alt_text": "SmartAPI"
            }
            blocks.append(body)

        if self._id:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "View details"
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Click Here",
                    },
                    "value": "registry_click",
                    "url": "http://smart-api.info/registry?q=" + self._id,
                    "action_id": "button-action"
                }
            })
        return {
            "attachments": [{
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
    print(response)

if __name__ == '__main__':
    test_slack()