from django.shortcuts import render, HttpResponse, redirect
import base64
import re
from django.contrib import messages
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.views import LoginView 
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .forms import EditProfileForm
from .utils import detect_sleep_from_frame
from .forms import ContactForm
from django.core.mail import send_mail
from django.conf import settings
from .models import Profile
import logging

logger = logging.getLogger(__name__)

class CustomLoginView(LoginView):
    template_name = 'login.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.request.user
        # Ensure the user has a profile
        if not hasattr(user, 'profile'):
            Profile.objects.create(user=user)
            messages.info(self.request, 'A profile was automatically created for you.')
        return response

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)

# Create your views here.

def home_page(request):
    return render(request, "Home.html")

def myprofile(request):
    return HttpResponse("This is my pfp")

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')  # Redirect to home page after successful login
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

def guest_login(request):
    # Maybe implement any guest-specific logic
    # For now, we'll just redirect to the home page
    return redirect('home')

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')  # Redirect to dashboard after signup
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})


def features(request):
    return render(request, 'features.html')

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            
            full_message = f"Message from {name} ({email}):\n\n{message}"
            
            # Send email (ensure email settings are configured in settings.py)
            try:
                send_mail(
                    subject,
                    full_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.CONTACT_EMAIL],  # Define CONTACT_EMAIL in settings.py
                    fail_silently=False,
                )
                messages.success(request, 'Your message has been sent successfully!')
            except Exception as e:
                messages.error(request, 'There was an error sending your message. Please try again later.')
            return redirect('contact')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})

@login_required
def dashboard(request):
    # Your dashboard logic
    return render(request, 'dashboard.html')

@login_required  # Ensures only authenticated users can access the analytics page
def analytics(request):
    # Placeholder data; replace with actual analytics data processing
    context = {
        'analytics_data': 'This is where your analytics data will be displayed.',
    }
    return render(request, 'analytics.html', context)

@login_required
def profile(request):
    # Implement profile view logic
    context = {
        'user': request.user,
        # Add more context data as needed
    }
    return render(request, 'profile.html', context)

@login_required
def settings_view(request):
    if request.method == 'POST':
        # Handle profile updates
        avatar = request.FILES.get('avatar')
        status = request.POST.get('status')
        description = request.POST.get('description')

        if avatar:
            request.user.profile.avatar = avatar
        if status:
            request.user.profile.status = status
        if description:
            request.user.profile.description = description

        request.user.profile.save()

        messages.success(request, 'Settings updated successfully!')
        return redirect('settings')
    
    # For GET requests, render the settings form
    context = {
        'user': request.user,
    }
    return render(request, 'settings.html', context)

# Edit Profile view
@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = EditProfileForm(instance=request.user)

    return render(request, 'edit_profile.html', {'form': form})

# Change Password view
@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keep the user logged in after password change
            return redirect('profile')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'change_password.html', {'form': form})

@csrf_exempt
def detection(request):
    if request.method == 'POST':
        logger.info("Received request data: %s", request.body)
        data = request.body.decode('utf-8')
        try:
            image_data = re.search(r'base64,(.*)', data).group(1)
            # Call the sleep detection function
            detection_result = detect_sleep_from_frame(image_data)

            # Return the results as JSON
            return JsonResponse({
                "status": detection_result["status"],
                "ear": detection_result["ear"],  # Return the EAR
                "left_eye": detection_result["left_eye"],  # Return left eye coordinates
                "right_eye": detection_result["right_eye"],  # Return right eye coordinates
            })
        except Exception as e:
            return HttpResponseBadRequest("Invalid image data")
    else:
        return render(request, 'detection_page.html')
