"""
URL configuration for realEstate project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = 'Real Estate'
admin.site.site_title = 'Real Estate'
admin.site.index_title = 'Real Estate'
urlpatterns = [
    path('super-admin/admin/', admin.site.urls),
    path('account/', include('account.urls')),
    path('booking-form/', include('bookingForm.urls')),
    path('misc/', include('propertyStatus.urls')),
    path('profile/', include('profileSearch.urls')),
    path('client-loan/', include('clientLoan.urls')),
    path('project-faq/', include('faq.urls')),
    path('social/', include('social.urls')),
    path('documentation/', include('documentation.urls')),
    path('admin-leads/', include('adminleads.urls')),
    path('whats-app/', include('sendwhatsappmessage.urls')),
    path('agent-report/', include('agentReport.urls')),
    path('lead-report/', include('leadReport.urls')),
    path('fest/', include('festival.urls')),
    path('mail/', include('sendEmails.urls')),
    path('data-upload/', include('DataUpload.urls')),
    path('site/', include('workers.urls')),
    path('ticket/', include('tickets.urls')),
    path('docx/', include('docx_gen.urls')),
    path('admin-pannel/', include('adminPannel.urls')),
    path('contact/', include('contactus.urls')),
    path('overview/', include('overview.urls')),
    path('agent-management/', include('agentmanagement.urls')),
    path('excel-files/', include('excelfiles.urls')),
    path('civil-worker/', include('civilWorker.urls')),
    path('development/', include('bills.urls')),
    
]+static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
