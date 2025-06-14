from django.db import models
from accounts.models import User
from domains.models import TechDomain

# Create your models here.

class TechBuddy(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    ]
    
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='buddy_requests_sent')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='buddy_requests_received')
    shared_domains = models.ManyToManyField(TechDomain, blank=True)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('requester', 'receiver')

    def __str__(self):
        return f"{self.requester.username} -> {self.receiver.username} ({self.status})"
