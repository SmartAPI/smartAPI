"""
    API Registration Slack Notification Message
    https://api.slack.com/messaging/composing/layouts
"""


class SlackNewAPIMessage():

    def __init__(self, _id, name, description, username):
        self._id = _id
        self.name = name
        self.description = description
        self.username = username

    def get_notification(self):
        return f":large_blue_circle: New API Registered: {self.name}"

    def get_header(self):
        return {
            "type": "plain_text",
            "text": ":large_blue_circle: New API Registered",
            "emoji": True
        }

    def get_body(self):
        return {
            "type": "mrkdwn",
            "text": (
                f"*Name*: {self.name}\n"
                f"*Description*: {self.description}\n"
                f"*Registered by*: <https://github.com/{self.username}|{self.username}>"
            )
        }

    def get_footer(self):
        return [
            {"type": "image", "image_url": "https://smart-api.info/static/img/owl-fly.gif", "alt_text": "SmartAPI"},
            {"type": "mrkdwn", "text": f"<https://smart-api.info/registry?q={self._id}|View on SmartAPI>"},
            {"type": "plain_text", "text": " | "},
            {"type": "mrkdwn", "text": ":book:"},
            {"type": "mrkdwn", "text": f"<https://smart-api.info/ui/{self._id}|View API Documentation>"}
        ]

    def compose(self):
        return {
            "text": self.get_notification(),
            "blocks": [
                {"type": "header", "text": self.get_header()},
                {"type": "section", "text": self.get_body()},
                {"type": "context", "elements": self.get_footer()}
            ]
        }


class SlackNewTranslatorAPIMessage(SlackNewAPIMessage):

    def get_notification(self):
        return f":large_purple_circle: New API Registered: {self.name}"

    def get_header(self):
        return {
            "type": "plain_text",
            "text": ":large_purple_circle: New Translator API Registered",
            "emoji": True
        }


# -------------
#    Tests
# -------------


def test_slack():
    """ test slack notification on main channel """
    import requests
    from config import SLACK_WEBHOOKS
    message = SlackNewAPIMessage("0xTEST", "MyAPI", "An API.", "tester")
    response = requests.post(SLACK_WEBHOOKS[0]["webhook"], json=message.compose())
    print(response.status_code)
    print(response.text)


if __name__ == '__main__':
    test_slack()
