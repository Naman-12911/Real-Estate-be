from django.contrib import messages
from django.conf import settings
from mailchimp_marketing import Client
from mailchimp_marketing.api_client import ApiClientError
import mailchimp_transactional as MailchimpTransactional


def mass_email(email_list, message):
    
    for email in email_list:
        mailchimp = Client()
        mailchimp.set_config({
            "api_key": settings.MAILCHIMP_API_KEY,
            "server": 'us7',
        })

        member_info = {
            "email_address": email,
            "status": "subscribed",
        }

        try:
            response = mailchimp.lists.add_list_member(settings.MAILCHIMP_EMAIL_LIST_ID, member_info)
            mailchimp = MailchimpTransactional.Client("YOUR_API_KEY")
            response = mailchimp.messages.send_raw({"raw_message": message})
            print("response: {}".format(response))
        except ApiClientError as error:
            print("An exception occurred: {}".format(error.text))
    
    return "Done"