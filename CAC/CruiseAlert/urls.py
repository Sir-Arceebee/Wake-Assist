from django.urls import path
from . import views
from .views import login_view
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", views.home_page, name= 'home'),
    path('detect/', views.detection_page, name='detection_page'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('features/', views.features, name='features'),
    path('contact/', views.contact, name='contact'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/change_password/', views.change_password, name='change_password'),
    path("detection/", views.detection, name="Processing"),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('guest-login/', views.guest_login, name='guest_login'),
    path('signup/', views.signup_view, name='signup'),
    
]
