from django.contrib import admin

# Register your models here.
from . import models

@admin.register(models.Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'resource_type', 'domain', 'uploaded_by', 'is_approved', 'created_at')
    list_filter = ('resource_type', 'domain', 'is_approved', 'created_at')
    search_fields = ('title', 'description', 'tags')
    actions = ['approve_resources', 'disapprove_resources']
    
    def approve_resources(self, request, queryset):
        queryset.update(is_approved=True)
    approve_resources.short_description = "Approve selected resources"
    
    def disapprove_resources(self, request, queryset):
        queryset.update(is_approved=False)
    disapprove_resources.short_description = "Disapprove selected resources"
