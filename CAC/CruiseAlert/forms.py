from django import forms
from django.contrib.auth.models import User

# Custom Edit Profile Form
class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']  # Fields you want to display
