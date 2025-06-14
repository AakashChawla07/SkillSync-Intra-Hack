from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'college_email', 'role', 'year_of_study', 'is_profile_complete')
    list_filter = ('role', 'year_of_study', 'is_profile_complete', 'is_staff')
    search_fields = ('username', 'email', 'college_email', 'first_name', 'last_name')
    
    fieldsets = UserAdmin.fieldsets + (
        ('College Information', {
            'fields': ('college_email', 'phone_number', 'year_of_study', 'branch', 'role')
        }),
        ('Profile', {
            'fields': ('bio', 'github_profile', 'linkedin_profile', 'profile_picture', 'is_profile_complete')
        }),
    )
