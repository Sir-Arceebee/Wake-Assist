from django.urls import path
from . import views
from .views import login_view
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", views.home_page, name= 'home'),
    path("myprofile", views.myprofile, name="profile"),
    path("detection/", views.detection, name="Processing"),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('guest-login/', views.guest_login, name='guest_login'),
    path('signup/', views.signup_view, name='signup'),
    
]
