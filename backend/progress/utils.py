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
        [user.email],
        fail_silently=True,
    )

def get_tech_buddy_recommendations(user):
    """Get tech buddy recommendations based on shared domains and goals"""
    from accounts.models import User
    from domains.models import UserDomain
    from network.models import TechBuddy
    from django.db.models import Q
    
    user_domains = UserDomain.objects.filter(
        user=user, 
        is_active=True
    ).values_list('domain_id', flat=True)
    
    potential_buddies = User.objects.filter(
        userdomain__domain_id__in=user_domains,
        userdomain__is_active=True
    ).exclude(id=user.id).distinct()
    
    existing_connections = TechBuddy.objects.filter(
        Q(requester=user) | Q(receiver=user)
    ).values_list('requester_id', 'receiver_id')
    
    connected_users = set()
    for req_id, rec_id in existing_connections:
        connected_users.add(req_id if req_id != user.id else rec_id)
    
    potential_buddies = potential_buddies.exclude(id__in=connected_users)
    
    return potential_buddies[:5]

def calculate_domain_activity_score(user, domain):
    """Calculate user's activity score in a domain"""
    from progress.models import Goal, GoalTask
    from resources.models import Resource
    from datetime import timedelta
    
    score = 0
    week_ago = date.today() - timedelta(days=7)
    
    recent_goals = Goal.objects.filter(
        user=user, 
        domain=domain,
        created_at__date__gte=week_ago
    ).count()
    score += recent_goals * 10
    
    recent_tasks = GoalTask.objects.filter(
        goal__user=user,
        goal__domain=domain,
        completed_at__date__gte=week_ago
    ).count()
    score += recent_tasks * 5
    
    recent_resources = Resource.objects.filter(
        uploaded_by=user,
        domain=domain,
        created_at__date__gte=week_ago
    ).count()
    score += recent_resources * 15
    
    return score