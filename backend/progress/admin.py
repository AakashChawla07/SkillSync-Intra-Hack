from django.contrib import admin

# Register your models here.
from . import models

@admin.register(models.Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'domain', 'status', 'priority', 'progress_percentage', 'target_date','created_at')
    list_filter = ('status', 'priority', 'domain', 'created_at')
    search_fields = ('title', 'user__username', 'domain__name')

@admin.register(models.WeeklyProgressReport)
class WeeklyProgressReportAdmin(admin.ModelAdmin):
    list_display = ('user', 'week_start', 'week_end', 'goals_completed', 'tasks_completed')
    list_filter = ('week_start', 'created_at')
    search_fields = ('user__username',)
