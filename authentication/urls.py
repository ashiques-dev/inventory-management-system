from django.urls import path
from authentication.views import *

urlpatterns = [
    path('register/<str:role>/',
         UserRegistrationView.as_view(), name='user_register'),

    path('verify-otp/<str:uid>/<str:token>/',
         OtpVerifyView.as_view(), name='verify_otp'),
    path('resend-otp/<str:uid>/<str:token>/',
         ResendOtpView.as_view(), name='resend_otp'),

    path('forgot-password/',
         ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/<str:uid>/<str:token>/',
         ResetPasswordView.as_view(), name='reset_password'),

    path('login/<str:role>/', UserLoginView.as_view(), name='user_login'),

    path('refresh/', CustomTokenRefreshView.as_view(),
         name='token_refresh'),
]
