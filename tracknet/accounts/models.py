from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Domain(models.Model):
    name = models.CharField(max_length=100)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    domains = models.ManyToManyField(Domain)
    bio = models.TextField(blank=True)

class Goal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

