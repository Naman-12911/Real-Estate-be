from django.urls import path,include
from .views import *
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView

urlpatterns = [
     path('register/', Register.as_view(),name="register"),
     path('login/', Login.as_view(),name="login"),
     path('profile/',userData.as_view(),name="profile"),
     path('update-profile/',update_profile.as_view(),name="update_profile"),
     path('password_reset/', PasswordResetView.as_view(), name='account_password_reset'),
     path('password_reset/done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
     path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
     path('reset/done/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
     path('password_reset/', PasswordResetAPIView.as_view(), name='password_reset'),
     path('all-users/', AccountUsersApiview.as_view(), name='AccountUsersApiview'),
     path('user-holiday/', HolidayView.as_view(), name='HolidayView'),
     path('fcm-token/', FCMTokenView.as_view(), name='FCMTokenView'),
     path('sales-person/', AccountUsersSalesPersonApiview.as_view(), name='AccountUsersSalesPersonApiview'),
     path('deact-user/', DeactivateAccount.as_view(), name='DeactivateAccount'), # deactivate user
     path('deactivate-assigning/', AgentAssignAPI.as_view(), name='AgentAssignAPI'),
     path('all-tokens/', GetFMCTokens.as_view(), name='GetFMCTokens'),
     path('logout/', LogoutAPIView.as_view(), name='logout'),
     path('delete-account/', DeleteAccountAPIView.as_view(), name='DeleteAccountAPIView'),
     path('active-inactive-employee/', ActiveAndInActiveEmployee.as_view(), name='ActiveAndInActiveEmployee'),
]
