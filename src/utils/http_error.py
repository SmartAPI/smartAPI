from typing import Optional, Any
from tornado.web import HTTPError
import re


class SmartAPIHTTPError(HTTPError):
    """An extended HTTPError class with additional details and message sanitization.

    Adds the following enhancements:
    - A `details` parameter for including extra context about the error.
    - A `clean_error_message` method for sanitizing log messages and details.

    :arg str details: Additional information about the error.
    """

    def __init__(
        self,
        status_code: int = 500,
        log_message: Optional[str] = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(status_code, log_message, *args, **kwargs)
        if self.reason:
            self.reason = self.clean_error_message(self.reason)
        if self.log_message:
            self.log_message = self.clean_error_message(self.log_message)

    @staticmethod
    def clean_error_message(message: str) -> str:
        """
        Sanitizes an error message by replacing newlines, tabs, and reducing multiple spaces.

        :param message: The error message to sanitize.
        :return: A cleaned and sanitized version of the message.
        """
        message = message.replace("\n", " ")  # Replace actual newlines with spaces
        message = re.sub(r'\s+', ' ', message)  # Normalize spaces
        return message.strip()
