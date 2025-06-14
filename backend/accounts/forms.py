from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class UserRegistrationForm(UserCreationForm):
    college_email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('username', 'college_email', 'password1', 'password2')

class ProfileSetupForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone_number', 'year_of_study', 
                 'branch', 'bio', 'github_profile', 'linkedin_profile', 'profile_picture')

