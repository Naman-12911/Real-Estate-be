from django.urls import path,include
from .views import *


urlpatterns = [
    path('worker/', SiteWorkersAPIview.as_view(),name="SiteWorkersAPIview"),
    path('worker/<int:pk>/', SiteWorkersAPIview.as_view(),name="SiteWorkersAPIview"),

    path('worker/filter/', SiteWorkersData.as_view(),name="SiteWorkersData"),
    path("get/amount/", GetExpense.as_view(), name="GetExpense"),

    path('worker/patch/<int:pk>/', SiteVisitPatchAPIview.as_view(),name="SiteVisitPatchAPIview"),
    path('worker/file/', SiteWorkerFile.as_view(), name='SiteWorkerFile'),

    path('worker/target/amount/', SiteWorkersDataTotalReciviedTargetAmount.as_view(),name="SiteWorkersDataTotalReciviedTargetAmount"),

]
