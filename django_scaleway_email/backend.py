import base64
import json
from email.mime.base import MIMEBase

import requests
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import EmailMessage
from django.core.mail.backends.base import BaseEmailBackend


class ScalewayEmailException(Exception):
    """Scaleway Email API Exception"""


class EmailBackend(BaseEmailBackend):
    """
    Scaleway Email API Backend.

    https://www.scaleway.com/en/docs/managed-services/transactional-email/how-to/generate-api-keys-for-tem-with-iam/

    """

    API_VERSION = "v1alpha1"
    API_REGION = "fr-par"
    API_URL = f"https://api.scaleway.com/transactional-email/{API_VERSION}/regions/{API_REGION}/emails"

    ATTACHMENT_TYPES = [
        "application/ics",
        "application/pdf",
        "application/pkcs10",
        "application/pkcs7-mime",
        "application/pkcs7-signature",
        "application/vnd.ms-excel",
        "application/vnd.ms-powerpoint",
        "application/vnd.oasis.opendocument.spreadsheet",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "application/vnd.openxmlformats-officedocument.presentationml.slideshow",
        "application/vnd.openxmlformats-officedocument.presentationml.template",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.template",
        "application/x-pdf",
        "application/xml",
        "image/gif",
        "image/jpeg",
        "image/jpg",
        "image/png",
        "image/svg+xml",
        "text/calendar",
        "text/csv",
        "text/html",
        "text/plain",
        "text/xml",
    ]

    def __init__(self, fail_silently=False, **kwargs):
        """Init options from Django settings"""
        super().__init__(fail_silently=fail_silently, **kwargs)

        self.api_url = getattr(
            settings,
            "SCALEWAY_EMAIL_API_URL",
            self.API_URL,
        )

        self.project_id = getattr(settings, "SCALEWAY_EMAIL_PROJECT_ID", None)
        if self.project_id is None:
            raise ImproperlyConfigured("SCALEWAY_EMAIL_PROJECT_ID is required")

        self.api_key = getattr(settings, "SCALEWAY_EMAIL_API_KEY", None)
        if self.api_key is None:
            raise ImproperlyConfigured("SCALEWAY_EMAIL_API_KEY is required")

    def _prepare_message(self, message: EmailMessage) -> dict:
        """
        Create the JSON payload for the Scaleway API.

        """
        payload = {
            "from": {
                "email": message.from_email,
            },
            "to": [{"email": recipient} for recipient in message.to],
            "cc": [{"email": recipient} for recipient in message.cc],
            "bcc": [{"email": recipient} for recipient in message.bcc],
            "subject": message.subject,
            "text": message.body,
            "project_id": self.project_id,
            "additional_headers": [
                {
                    "key": key,
                    "value": value,
                }
                for key, value in message.extra_headers.items()
            ],
        }

        # Add the HTML version
        if message.alternatives:
            for alternative in message.alternatives:
                if alternative[1] == "text/html":
                    payload["html"] = alternative[0]
                    break

        if message.reply_to:
            payload["additional_headers"].extend(
                [
                    {
                        "key": "Reply-To",
                        "value": email,
                    }
                    for email in message.reply_to
                ]
            )

        if message.attachments:
            payload["attachments"] = []
            for attachment in message.attachments:
                if isinstance(attachment, MIMEBase):
                    filename = attachment.get_filename()
                    mimetype = attachment.get_content_type()
                    content = attachment.get_payload(decode=True)
                else:
                    filename, content, mimetype = attachment
                    if isinstance(content, str):
                        content = content.encode()

                if mimetype not in self.ATTACHMENT_TYPES:
                    raise ScalewayEmailException(
                        f"Attachment {filename} has an disallowed content type: {mimetype}"
                    )

                payload["attachments"].append(
                    {
                        "name": filename,
                        "type": mimetype,
                        "content": base64.b64encode(content).decode(),
                    }
                )

        return payload

    def _post(self, payload: dict) -> dict:
        """Send a POST request to the Scaleway API."""
        response = requests.post(
            self.api_url,
            json=payload,
            headers={"X-Auth-Token": self.api_key},
        )
        if response.status_code != 200:
            raise ScalewayEmailException(
                f"Scaleway API Error {response.status_code}: {response.text}"
            )
        return response.json()

    def send_messages(self, email_messages: list[EmailMessage]) -> int:
        """
        Send messages using the Scaleway API.

        :return: Number of successfully sent messages

        """
        if not email_messages:
            return
        msg_count = 0
        try:
            client_created = self.open()
            for message in email_messages:
                payload = self._prepare_message(message)
                response = self._post(payload)
                msg_count += len(response["emails"])
            if client_created:
                self.close()
        except Exception:
            if not self.fail_silently:
                raise
        return msg_count
