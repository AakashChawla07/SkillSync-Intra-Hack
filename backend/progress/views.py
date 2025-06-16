from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import date, timedelta
from .models import Goal, GoalTask, WeeklyProgressReport
from domains.models import TechDomain, UserDomain

# Create your views here.

@login_required
def progress_dashboard(request):
    goals = Goal.objects.filter(user=request.user).select_related('domain').order_by('-created_at')
    
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    weekly_report = WeeklyProgressReport.objects.filter(
        user=request.user,
        week_start=week_start
    ).first()
    
    
    total_goals = goals.count()
    completed_goals = goals.filter(status='completed').count()
    in_progress_goals = goals.filter(status='in_progress').count()
    
    context = {
        'goals': goals,
        'weekly_report': weekly_report,
        'total_goals': total_goals,
        'completed_goals': completed_goals,
        'in_progress_goals': in_progress_goals,
    }
    
    return render(request, 'progress/dashboard.html', context)

@login_required
def create_goal(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        domain_name = request.POST.get('domain_name')
        priority = request.POST.get('priority')
        target_date = request.POST.get('target_date')
        
        domain = get_object_or_404(TechDomain, name=domain_name)
        
        goal = Goal.objects.create(
            user=request.user,
            domain=domain,
            title=title,
            description=description,
            priority=priority,
            target_date=target_date
        )
        
        tasks = request.POST.getlist('tasks[]')
        for task_title in tasks:
            if task_title.strip():
                GoalTask.objects.create(
                    goal=goal,
                    title=task_title.strip()
                )
        
        messages.success(request, 'Goal created successfully!')
        return redirect('progress_dashboard')
    
    user_domains = UserDomain.objects.filter(
        user=request.user, 
        is_active=True
    ).select_related('domain')
    
    context = {
        'user_domains': user_domains,
        'priority_choices': Goal.PRIORITY_CHOICES,
    }
    
    return render(request, 'progress/create_goal.html', context)

@login_required
def goal_detail(request, goal_id):
    goal = get_object_or_404(Goal, id=goal_id, user=request.user)
    tasks = goal.tasks.all().order_by('created_at')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_progress':
            progress = int(request.POST.get('progress', 0))
            goal.progress_percentage = progress
            if progress == 100:
                goal.status = 'completed'
                goal.completed_at = timezone.now()
            elif progress > 0:
                goal.status = 'in_progress'
            goal.save()
            messages.success(request, 'Progress updated!')
        
        elif action == 'toggle_task':
            task_id = request.POST.get('task_id')
            task = get_object_or_404(GoalTask, id=task_id, goal=goal)
            task.is_completed = not task.is_completed
            if task.is_completed:
                task.completed_at = timezone.now()
            else:
                task.completed_at = None
            task.save()
            
            total_tasks = tasks.count()
            completed_tasks = tasks.filter(is_completed=True).count()
            if total_tasks > 0:
                progress = int((completed_tasks / total_tasks) * 100)
                goal.progress_percentage = progress
                if progress == 100:
                    goal.status = 'completed'
                    goal.completed_at = timezone.now()
                elif progress > 0:
                    goal.status = 'in_progress'
                goal.save()
        
        return redirect('goal_detail', goal_id=goal.id)
    
    context = {
        'goal': goal,
        'tasks': tasks,
    }
    
    return render(request, 'progress/goal_detail.html', context)
