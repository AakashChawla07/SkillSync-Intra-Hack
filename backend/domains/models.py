from django.db import models

# Create your models here.
from accounts.models import User

class TechDomain(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=50, help_text="Font Awesome icon class")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def get_member_count(self):
        return UserDomain.objects.filter(domain=self, is_active=True).count()

    def get_resource_count(self):
        return self.resources.filter(is_approved=True).count()

class UserDomain(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    domain = models.ForeignKey(TechDomain, on_delete=models.CASCADE)
    skill_level = models.CharField(max_length=20, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert')
    ])
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    goals = models.TextField(blank=True, help_text="Personal learning goals in this domain")

    class Meta:
        unique_together = ('user', 'domain')

    def __str__(self):
        return f"{self.user.username} - {self.domain.name}"

class DomainRecognition(models.Model):
    RECOGNITION_TYPES = [
        ('helpful_mentor', 'Most Helpful Mentor'),
        ('active_contributor', 'Active Contributor'),
        ('project_champ', 'Project Champ'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    domain = models.ForeignKey(TechDomain, on_delete=models.CASCADE)
    recognition_type = models.CharField(max_length=30, choices=RECOGNITION_TYPES)
    week_start = models.DateField()
    week_end = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'domain', 'recognition_type', 'week_start')

    def __str__(self):
        return f"{self.user.username} - {self.get_recognition_type_display()} - {self.domain.name}"