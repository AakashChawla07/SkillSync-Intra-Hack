from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

# Create your models here.
class User(AbstractUser):
    YEAR_CHOICES = [
        ('1', 'First Year'),
        ('2', 'Second Year'),
        ('3', 'Third Year'),
        ('4', 'Fourth Year'),
        ('alumni', 'Alumni'),
    ]
    
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('mentor', 'Mentor'),
        ('admin', 'Admin'),
    ]
    def validate_thapar_email(value):
        if not value.lower().endswith('@thapar.edu'):
            raise ValidationError("Email must be a College email (ending with @thapar.edu).")
        else:
            return value
    
    
    college_email = models.EmailField(validators=[validate_thapar_email],unique=True)
    phone_number = models.CharField(max_length=15, blank=True)
    year_of_study = models.CharField(max_length=10, choices=YEAR_CHOICES)
    branch = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    bio = models.TextField(max_length=500, blank=True)
    github_profile = models.URLField(blank=True)
    linkedin_profile = models.URLField(blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    is_profile_complete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"