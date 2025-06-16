from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Project, User

class UserRegistrationForm(UserCreationForm):
    college_email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('username', 'college_email', 'password1', 'password2')

class ProfileSetupForm(forms.ModelForm):
    class Meta:
        model = User
        current_focus = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter skills separated by commas (e.g., React.js, Python, UI/UX)',
            'class': 'mt-1 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md'
        }),
        required=False,
        help_text='Separate skills with commas'
        )
        fields = ('first_name', 'last_name', 'phone_number', 'year_of_study','branch', 'bio', 'github_profile', 'linkedin_profile', 'profile_picture','current_focus')
        def __init__(self, *args, **kwargs):
            self.user = kwargs.pop('user', None)
            super().__init__(*args, **kwargs)
            if self.instance and self.instance.current_focus:
                self.fields['current_focus'].initial = ', '.join(self.instance.current_focus)
            
        def save(self, commit=True):
            profile = super().save(commit=False)
        
        # Handle current_focus as list
            focus_text = self.cleaned_data.get('current_focus', '')
            if focus_text:
                profile.current_focus = [skill.strip() for skill in focus_text.split(',') if skill.strip()]
            else:
                profile.current_focus = []
            
            if commit:
                profile.save()
            return profile
    
class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('title', 'description', 'category', 'project_url')
        
       