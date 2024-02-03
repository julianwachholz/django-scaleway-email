# Django Scaleway Email

A small Django package that allows you to use [Scaleway's transactional email](https://www.scaleway.com/en/transactional-email-tem/) API.

## Requirements

To use this backend, you need an account with Scaleway and follow their [setup guide
for the transactional email service](https://www.scaleway.com/en/docs/managed-services/transactional-email/quickstart/).

You can then [create an IAM Application](https://console.scaleway.com/iam/applications) and generate a new API key for it.
Ensure the application has the `TransactionalEmailEmailFullAccess` permission.

## Installation

1. Install the package with your package manager of choice:

   ```bash
   pip install django-scaleway-email
   ```

2. Set your `EMAIL_BACKEND` and configure your secrets:

   ```python
   EMAIL_BACKEND = "django_scaleway_email.backend.EmailBackend"
   SCALEWAY_EMAIL_PROJECT_ID = "your-project-id"
   SCALEWAY_EMAIL_API_KEY = "your-api-key"
   ```

3. Done! You can now use `django.core.mail.send_mail` etc. to send emails!

## Limitations

Scaleway imposes a few [limitations on emails](https://www.scaleway.com/en/docs/managed-services/transactional-email/reference-content/tem-capabilities-and-limits/). Here's a short summary:

- Max. 3 recipients per email
- Max. 2 attachments
- Max. total email size is 2 MB
- Only PDF, images and plaintext attachments allowed
