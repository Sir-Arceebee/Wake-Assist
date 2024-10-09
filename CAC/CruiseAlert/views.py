from django.shortcuts import render, HttpResponse, redirect
import base64
import re
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .forms import EditProfileForm
from .utils import detect_sleep_from_frame
import logging

logger = logging.getLogger(__name__)

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
            return redirect('home')  # Redirect to home page after successful login
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
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

def detection_page(request):
    return render(request, 'detection_page.html')

def features(request):
    return render(request, 'features.html')

def contact(request):
    return render(request, 'contact.html')

def dashboard_view(request):
    context = {
        'user': request.user,
        'drowsiness_chart': None,  # Replace with chart URL or None if no data
        'sleep_chart': None,  # Replace with chart URL or None if no data
        'recent_sessions': [
            {'date': 'April 10', 'level': 'High'},
            {'date': 'April 08', 'level': 'Medium'},
        ],  # Pass empty list if no sessions
        'notifications': [],
        'activity_log': [],
        'todo_list': ['Complete Sleep Survey', 'Update Profile Information'],
    }
    return render(request, 'dashboard.html', context)

# Profile view
@login_required
def profile(request):
    return render(request, 'profile.html')  # Renders the profile page template

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
            # Handle exceptions (e.g., if image_data is not found)
            return HttpResponseBadRequest("Invalid image data")

    else:
        # Handle GET request - redirect to the detection page or show a friendly message
        return redirect('detection_page')  # Redirect to the detection page
