from django.db import models

# Create your models here.
from accounts.models import User
from domains.models import TechDomain

class Resource(models.Model):
    RESOURCE_TYPES = [
        ('tutorial', 'Tutorial'),
        ('documentation', 'Documentation'),
        ('video', 'Video'),
        ('project', 'Project'),
        ('roadmap', 'Roadmap'),
        ('opportunity', 'Opportunity'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    domain = models.ForeignKey(TechDomain, on_delete=models.CASCADE, related_name='resources')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.URLField(blank=True, help_text="External link to resource")
    file = models.FileField(upload_to='resources/', blank=True, null=True)
    tags = models.CharField(max_length=200, blank=True, help_text="Comma-separated tags")
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.domain.name}"

    def get_tags_list(self):
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]

class ResourceBookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'resource')