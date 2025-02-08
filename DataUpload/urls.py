from django.urls import path,include
from .views import *


urlpatterns = [
    path('file/', FileUploadView.as_view(),name="FileUploadView"),
    path('file-new/', LeadEditUploadViewNew.as_view(),name="FileUploadView"),
    # path('file-fbleads/', FBLeadUploadViewNew.as_view(),name="FileUploadView"),
    # path('file-dicussion/', UploadDiscussion.as_view(),name="UploadDiscussion"),
    path('old-notification',OldNotificationAPI.as_view(), name="OldNotificationAPI"),
    path('data_update',LeadEditUpdate.as_view(), name="LeadEditUpdate"),
    # path('feedback-update',UpdateLeadFeedback.as_view(), name="UpdateLeadFeedback"),
    # path('notification-update',UpdateNoti.as_view(), name="UpdateNoti"),
    path('data-check', DataCheck.as_view(), name="DataCheck")
]