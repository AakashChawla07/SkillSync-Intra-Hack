from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.urls import reverse

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
    current_focus = models.JSONField(default=list, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    is_profile_complete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"
    def get_completion_percentage(self):
        # Calculate completion based on projects
        total_projects = self.projects.count()
        if total_projects == 0:
            return 0
        completed_projects = self.projects.filter(status='completed').count()
        return round((completed_projects / total_projects) * 100)
    
    def get_domain_count(self):
        # Get unique domains from projects
        domains = self.projects.values_list('category', flat=True).distinct()
        return len([d for d in domains if d])
    
class Project(models.Model):
    
    user_profile = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=200)
    description = models.TextField()
    project_url = models.URLField(blank=True, null=True)
    category = models.CharField(max_length=20,default='other')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return self.project_url

class Domain(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class UserDomain(models.Model):
    user_profile = models.ForeignKey(User, on_delete=models.CASCADE, related_name='domains')
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)
    progress_percentage = models.IntegerField(default=0)
    peers_count = models.IntegerField(default=0)
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user_profile', 'domain')
    
    def __str__(self):
        return f"{self.user_profile.user.username} - {self.domain.name}"
