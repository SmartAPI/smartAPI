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
        return f"A new API has been registered on Smart-API.info: {self.name}"

    def get_header(self):
        return {
            "type": "mrkdwn",
            "text": "A new API has been registered on Smart-API.info:",
        }

    def get_body(self):
        return {
            "type": "mrkdwn",
            "text": (
                f"*Title*: {self.name}\n"
                f"*Description*: {self.description}\n"
                f"*Registered by*: <https://github.com/{self.username}|{self.username}>"
            )
        }

    def get_footer(self):
        return [
            {"type": "mrkdwn", "text": f"<https://smart-api.info/registry?q={self._id}|View on SmartAPI>"},
            {"type": "plain_text", "text": " | "},
            {"type": "mrkdwn", "text": f"<https://smart-api.info/ui/{self._id}|View API Documentation>"}
        ]

    def compose(self):
        return {
            "text": self.get_notification(),
            "blocks": [
                {"type": "section", "text": self.get_header()},
                {"type": "section", "text": self.get_body()},
                {"type": "context", "elements": self.get_footer()}
            ]
        }


class SlackNewTranslatorAPIMessage(SlackNewAPIMessage):

    def get_notification(self):
        return f"A new Translator API has been registered on Smart-API.info: {self.name}"

    def get_header(self):
        return {
            "type": "mrkdwn",
            "text": "A new Translator API has been registered on Smart-API.info:",
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
