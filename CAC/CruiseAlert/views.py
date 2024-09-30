from django.shortcuts import render, HttpResponse, redirect
import base64
import re
import numpy as np
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from .utils import detect_sleep_from_frame


# Create your views here.
def home(request):
    return HttpResponse("hello world!")

def myprofile(request):
    return HttpResponse("This is my pfp")

def detection_page(request):
    return render(request, 'detection_page.html')  # Ensure this path is correct

@csrf_exempt
def detection(request):
    if request.method == 'POST':
        data = request.body.decode('utf-8')
        try:
            image_data = re.search(r'base64,(.*)', data).group(1)
            status = detect_sleep_from_frame(image_data)
            return JsonResponse({"status": status})
        except Exception as e:
            # Handle exceptions (e.g., if image_data is not found)
            return HttpResponseBadRequest("Invalid image data")

    else:
        # Handle GET request - redirect to the detection page or show a friendly message
        return redirect('detection_page')  # Redirect to the main page or a custom page
