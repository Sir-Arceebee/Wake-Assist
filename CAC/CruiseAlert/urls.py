from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_page, name= 'Home'),
    path("detect", views.detection_page, name='detection_page'),
    path("myprofile", views.myprofile, name = "Profile_Page"),
    path("detection", views.detection, name = "Processing")
]
