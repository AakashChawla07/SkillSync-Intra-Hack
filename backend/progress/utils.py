from django.core.mail import send_mail
from django.conf import settings
from datetime import date, timedelta
import random

def send_weekly_motivation_email(user, report):
    """Send weekly motivation email to users"""
    subject = f"SkillSync Weekly Progress - {user.get_full_name() or user.username}"
    
    message = f"""
    Hi {user.get_full_name() or user.username},
    
    Here's your weekly progress summary:
    
    Goals Completed: {report.goals_completed}
    Tasks Completed: {report.tasks_completed}
    Active Domains: {', '.join([d.name for d in report.domains_active.all()])}
    
    {report.motivational_message}
    
    Suggestion: {report.suggestions}
    
    Keep up the great work!
    
    Best regards,
    The SkillSync Team
    """
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.college_email],
        fail_silently=True,
    )
