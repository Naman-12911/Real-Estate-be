# utils/mailchimp_utils.py

import mailchimp_marketing as MailchimpClient
from django.conf import settings

def send_email_to_subscribers(subject, message):
    mailchimp = MailchimpClient.Client()
    mailchimp.set_config({
        "api_key": settings.MAILCHIMP_API_KEY,
        "server": settings.Mailchimp_DATACENTER
    })

    # Example: Sending email to subscribers
    # Replace 'your_list_id' with your actual Mailchimp audience ID
    try:
        response = mailchimp.lists.send_campaign(
            "your_list_id",
            {
                "subject_line": subject,
                "preview_text": message,
                "recipients": {
                    "list_id": settings.Mailchimp_LIST_ID
                },
                "type": "regular",
                "settings": {
                    "subject_line": subject,
                    "preview_text": message,
                    "title": subject,
                    "from_name": "Your Name",
                    "reply_to": "your@email.com"
                }
            }
        )
        return response
    except Exception as e:
        return str(e)
