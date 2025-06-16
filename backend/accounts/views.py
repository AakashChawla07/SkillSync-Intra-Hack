import random
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.db.models import  Q,Count
from collections import defaultdict
from django.contrib import messages
from django.urls import reverse_lazy
from datetime import date, timedelta
from domains.models import TechDomain, UserDomain, DomainRecognition
from progress.models import Goal, WeeklyProgressReport
from resources.models import Resource
from network.models import TechBuddy
from .forms import UserRegistrationForm, ProfileSetupForm
from .models import User

# Create your views here.

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['college_email']
            user.save()
            login(request, user)
            messages.success(request, 'Registration successful! Please complete your profile.')
            return redirect('profile_setup')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def profile_setup(request):
    if request.method == 'POST':
        form = ProfileSetupForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_profile_complete = True
            user.save()
            messages.success(request, 'Profile setup completed!')
            return redirect('dashboard')
    else:
        form = ProfileSetupForm(instance=request.user)
    return render(request, 'accounts/profile_setup.html', {'form': form})

@login_required
def profile_view(request, username=None):
    """
    Display user profile page with projects and activity data
    """
    if username:
        # Viewing someone else's profile
        profile_user = get_object_or_404(User, username=username)
    else:
        # Viewing own profile
        profile_user = request.user
    
    # Get activity data for the chart (last 7 days)
    # activity_data = get_user_activity_data(profile_user)
    
    # Get upcoming events (you'll need to implement this based on your Event model)
    # //upcoming_events = get_upcoming_events(profile_user)
    
    context = {
        'user': profile_user,
        # 'activity_data': json.dumps(activity_data),
        # 'upcoming_events': upcoming_events,
        'is_own_profile': request.user == profile_user,
    }
    
    return render(request, 'accounts/profile.html', context)


@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        # Handle form submission
        # You'll implement the form handling here
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    
    return render(request, 'accounts/profile_setup.html', {'user': request.user})

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('dashboard')  # Add success URL
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Login - SkillSync'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Welcome back! You have successfully logged in.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Invalid email or password. Please try again.')
        return super().form_invalid(form)


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard_home(request):
    user = request.user
    
    if not user.is_profile_complete:
        return redirect('profile_setup')
    
    # Get user domains with their skill levels
    user_domains = UserDomain.objects.filter(
        user=user, 
        is_active=True
    ).select_related('domain')
    
    # Get active goals (limiting to 5 most recent)
    active_goals = Goal.objects.filter(
        user=user,
        status__in=['not_started', 'in_progress']
    ).select_related('domain').order_by('-created_at')[:5]
    
    # Get popular domains with member counts and recent members
    popular_domains_data = []
    domains_with_members = UserDomain.objects.filter(
        is_active=True
    ).values('domain').annotate(
        member_count=Count('user', distinct=True)
    ).order_by('-member_count')[:6]  # Get top 6 popular domains
    
    # Define available colors for random assignment
    available_colors = ['blue', 'green', 'purple', 'red', 'yellow', 'indigo', 'pink', 'teal', 'orange', 'cyan']
    
    # Default icon path for all domains
    default_icon_path = 'M13 10V3L4 14h7v7l9-11h-7z'  # Lightning bolt icon
    
    for i, domain_data in enumerate(domains_with_members):
        try:
            domain = TechDomain.objects.get(id=domain_data['domain'])
            
            # Get recent members for this domain (limit to 3 for display)
            recent_members = User.objects.filter(
                userdomain__domain=domain,
                userdomain__is_active=True
            ).distinct()[:3]
            
            remaining_count = max(0, domain_data['member_count'] - 3)
            
            popular_domains_data.append({
                'domain': domain,
                'member_count': domain_data['member_count'],
                'recent_members': recent_members,
                'remaining_count': remaining_count,
                'color': random.choice(available_colors),
                'icon_path': default_icon_path
            })
        except TechDomain.DoesNotExist:
            continue
    
    # Get recent resources (from all domains, not just user's domains for broader discovery)
    recent_resources = Resource.objects.filter(
        is_approved=True
    ).select_related('domain', 'uploaded_by').order_by('-created_at')[:6]
    
    # Get weekly progress report
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    weekly_report = WeeklyProgressReport.objects.filter(
        user=user,
        week_start=week_start
    ).first()
    
    # Get tech buddies count
    buddies_count = TechBuddy.objects.filter(
        Q(requester=user, status='accepted') |
        Q(receiver=user, status='accepted')
    ).count()
    
    # Get current recognitions
    current_recognitions = DomainRecognition.objects.filter(
        user=user,
        week_start__lte=today,
        week_end__gte=today
    ).select_related('domain')
    
    # Calculate completion metrics
    total_goals = Goal.objects.filter(user=user).count()
    completed_goals = Goal.objects.filter(user=user, status='completed').count()
    completion_rate = (completed_goals / total_goals * 100) if total_goals > 0 else 0
    
    context = {
        'user': user,
        'user_domains': user_domains,
        'active_goals': active_goals,
        'popular_domains': popular_domains_data,  # Updated key name
        'recent_resources': recent_resources,
        'weekly_report': weekly_report,
        'buddies_count': buddies_count,
        'current_recognitions': current_recognitions,
        'total_goals': total_goals,
        'completed_goals': completed_goals,
        'completion_rate': completion_rate,
    }
    
    return render(request, 'dashboard/home.html', context)

@login_required
def add_project_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.user_profile = profile
            project.save()
            messages.success(request, 'Project added successfully!')
            return redirect('profile')
    else:
        form = ProjectForm()
    
    context = {
        'form': form,
        'title': 'Add Project - SkillSync'
    }
    
    return render(request, 'accounts/add_project.html', context)

@login_required
def delete_project_view(request, pk):
    if(request.method=='POST'):
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        project = get_object_or_404(Project, pk=pk, user_profile=profile)
        
        project_title = project.title
        project.delete()
        messages.success(request, f'Project "{project_title}" has been deleted.')
    
    return redirect('profile')
