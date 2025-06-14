from django.contrib import admin

# Register your models here.
from . import models
@admin.register(models.TechDomain)
class TechDomainAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'get_member_count', 'get_resource_count', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')

@admin.register(models.UserDomain)
class UserDomainAdmin(admin.ModelAdmin):
    list_display = ('user', 'domain', 'skill_level', 'joined_at', 'is_active')
    list_filter = ('skill_level', 'is_active', 'joined_at')
    search_fields = ('user__username', 'domain__name')

@admin.register(models.DomainRecognition)
class DomainRecognitionAdmin(admin.ModelAdmin):
    list_display = ('user', 'domain', 'recognition_type', 'week_start', 'week_end')
    list_filter = ('recognition_type', 'week_start')
    search_fields = ('user__username', 'domain__name')
