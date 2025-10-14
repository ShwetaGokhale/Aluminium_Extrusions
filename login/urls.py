from django.urls import path
from .views import LoginView, VerifyOTPView, RegisterView, LogoutView

urlpatterns = [
    # Login page — handles email entry and sending OTP
    path('', LoginView.as_view(), name='login'),

    # OTP verification — checks entered OTP and logs user in
    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),

    # Registration page — for new user signup
    path('register/', RegisterView.as_view(), name='register'),

    # Logout — clears session and redirects to login
    path('logout/', LogoutView.as_view(), name='logout'),
]
