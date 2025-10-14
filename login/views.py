from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.core.mail import send_mail
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import User
import random


def send_otp(email):
    """Helper function to generate and send OTP via email."""
    otp = str(random.randint(100000, 999999))
    subject = "Your Login OTP"
    message = f"Your OTP for login is: {otp}"
    send_mail(subject, message, "infitestmail2024@gmail.com", [email])
    return otp


class LoginView(View):
    """Handle user login and OTP sending."""

    def get(self, request):
        # Clear old session and messages on fresh load
        if 'email' in request.session:
            del request.session['email']
        
        # Clear any existing messages
        storage = messages.get_messages(request)
        storage.used = True
        
        return render(request, "login/login.html", {"show_otp": False})

    def post(self, request):
        email = request.POST.get("email")
        otp = request.POST.get("otp")

        # Case 1: Sending OTP (no OTP entered yet)
        if not otp:
            try:
                user = User.objects.get(email=email)
                generated_otp = send_otp(email)
                user.otp = generated_otp
                user.save()
                request.session["email"] = email
                messages.success(request, "OTP sent to your email.")
                return render(request, "login/login.html", {"show_otp": True, "email": email})
            except User.DoesNotExist:
                messages.error(request, "Email does not exist. Please register first.")
                return render(request, "login/login.html", {"email": email, "show_otp": False})

        # Case 2: If OTP entered, redirect to verification view
        return redirect("verify_otp")


class VerifyOTPView(View):
    """Handle OTP verification."""

    def post(self, request):
        email = request.session.get("email")
        otp = request.POST.get("otp")

        try:
            user = User.objects.get(email=email)
            if user.otp == otp:
                user.is_verified = True
                user.save()
                request.session["user"] = user.email
                messages.success(request, "Login successful!")
                return redirect("dashboard")
            else:
                messages.error(request, "Invalid OTP. Please try again.")
                return render(request, "login/login.html", {"show_otp": True, "email": email})
        except User.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect("login")

    def get(self, request):
        return redirect("login")


class RegisterView(View):
    """Handle user registration."""

    def get(self, request):
        return render(request, "login/register.html")

    def post(self, request):
        email = request.POST.get("email")

        # Check if already registered
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered. Please login instead.")
            return render(request, "login/register.html", {"email": email})
        else:
            User.objects.create(email=email)
            messages.success(request, "Registration successful! Please login to continue.")
            return redirect("login")


class LogoutView(View):
    """Handle user logout."""

    def get(self, request):
        # Clear all messages first
        storage = messages.get_messages(request)
        for _ in storage:
            pass
        storage.used = True
        
        # Then flush session
        request.session.flush()
        
        # Redirect to login without any messages
        return redirect("login")