import os
import pytest
import requests

from django.core.mail import send_mail, EmailMultiAlternatives
from django.core.exceptions import ImproperlyConfigured

from django_scaleway_email.backend import ScalewayEmailException


class MockResponse:
    status_code = 200

    def __init__(self, *args, json=None, **kwargs):
        self._json = json

    def json(self):
        # Count emails in payload
        email_count = sum(len(self._json.get(field)) for field in ["to", "cc", "bcc"])
        return {
            "dummy": True,
            "emails": [
                {
                    "id": "dummy-id",
                    "status": "sent",
                    "email": "",
                }
                for _ in range(email_count)
            ],
        }

    def raise_for_status(self):
        pass


@pytest.fixture
def mock_requests(monkeypatch):

    def mock_post(*args, **kwargs):
        return MockResponse(*args, **kwargs)

    monkeypatch.setattr(requests, "post", mock_post)


def _send_test_email():
    return send_mail(
        "Subject here",
        "Here is the message.",
        "postmaster@localhost",
        ["test@example.com"],
    )


def test_send_message(settings, mock_requests):
    """Test sending an email message."""
    settings.EMAIL_BACKEND = "django_scaleway_email.backend.EmailBackend"
    settings.SCALEWAY_EMAIL_PROJECT_ID = "dummy-project-id"
    settings.SCALEWAY_EMAIL_API_KEY = "dummy-api-key"

    assert _send_test_email() == 1


def test_send_message_multiple(settings, mock_requests):
    """Test sending an email message."""
    settings.EMAIL_BACKEND = "django_scaleway_email.backend.EmailBackend"
    settings.SCALEWAY_EMAIL_PROJECT_ID = "dummy-project-id"
    settings.SCALEWAY_EMAIL_API_KEY = "dummy-api-key"

    message = EmailMultiAlternatives(
        subject="Subject here",
        body="This message has three recipients.",
        from_email="postmaster@localhost",
        to=["test@example.com", "another@example.com"],
        cc=["carbon@copy.com"],
    )
    assert message.send() == 3


def test_scaleway_required_settings(settings, mock_requests):
    """Test sending an email message."""
    settings.EMAIL_BACKEND = "django_scaleway_email.backend.EmailBackend"

    with pytest.raises(ImproperlyConfigured):
        _send_test_email()

    settings.SCALEWAY_EMAIL_PROJECT_ID = "dummy-project-id"
    settings.SCALEWAY_EMAIL_API_KEY = None
    with pytest.raises(ImproperlyConfigured):
        _send_test_email()

    settings.SCALEWAY_EMAIL_PROJECT_ID = None
    settings.SCALEWAY_EMAIL_API_KEY = "dummy-api-key"
    with pytest.raises(ImproperlyConfigured):
        _send_test_email()


def test_scaleway_attachment_invalid_mime(settings, mock_requests):
    settings.EMAIL_BACKEND = "django_scaleway_email.backend.EmailBackend"
    settings.SCALEWAY_EMAIL_PROJECT_ID = "dummy-project-id"
    settings.SCALEWAY_EMAIL_API_KEY = "dummy-api-key"

    message = EmailMultiAlternatives(
        subject="Subject here",
        body="This message has an invalid attachment.",
        from_email="postmaster@localhost",
        to=["test@example.com"],
    )
    message.attach(
        filename="test.mp3",
        content=b"dummy-content",
        mimetype="audio/mpeg",
    )
    with pytest.raises(ScalewayEmailException) as exc_info:
        message.send()
    assert (
        str(exc_info.value)
        == "Attachment test.mp3 has an disallowed content type: audio/mpeg"
    )


def test_scaleway_email_real(settings):
    settings.EMAIL_BACKEND = "django_scaleway_email.backend.EmailBackend"

    try:
        settings.SCALEWAY_EMAIL_PROJECT_ID = os.environ["SCALEWAY_EMAIL_PROJECT_ID"]
        settings.SCALEWAY_EMAIL_API_KEY = os.environ["SCALEWAY_EMAIL_API_KEY"]
    except KeyError:
        pytest.skip("SCALEWAY_EMAIL_PROJECT_ID and SCALEWAY_EMAIL_API_KEY are required")

    from_email = os.environ["SCALEWAY_FROM_EMAIL"]
    to_email = os.environ["SCALEWAY_TO_EMAIL"]

    message = EmailMultiAlternatives(
        subject="Subject here",
        body="Here is the test message. Thank you.",
        from_email=from_email,
        to=[to_email],
        bcc=[from_email],
    )
    message.attach_alternative(
        """<p>Here is the test <a href="https://duckduckgo.com">message</a>.<br><br>Thank you.</p>""",
        "text/html",
    )

    message.attach(
        filename="example.txt",
        content="Here is the test message.\n\nThank you.",
        mimetype="text/plain",
    )
    num_sent = message.send()
    # Each recipient (TO, CC, BCC) counts as a separate email
    assert num_sent == 2
