from django.contrib import admin
from .models import SendMailToClients, MailTemplate
# Register your models here.

admin.site.register(SendMailToClients)
admin.site.register(MailTemplate)