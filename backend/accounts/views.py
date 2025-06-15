from django.shortcuts import redirect, render
from django.contrib.auth import login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.db.models import  Q
from django.contrib import messages
from datetime import date, timedelta
from domains.models import UserDomain, DomainRecognition
from progress.models import Goal, WeeklyProgressReport
from resources.models import Resource
from network.models import TechBuddy
from .forms import UserRegistrationForm, ProfileSetupForm
from .models import User

# Create your views here.

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.urls import reverse_lazy
from .forms import UserRegistrationForm, ProfileSetupForm

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
def profile_view(request):    
    return render(request, 'accounts/profile.html', {'user': request.user})

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
    
    
    user_domains = UserDomain.objects.filter(
        user=user, 
        is_active=True
    ).select_related('domain')
    
    
    active_goals = Goal.objects.filter(
        user=user,
        status__in=['not_started', 'in_progress']
    ).select_related('domain').order_by('-created_at')[:5]
    
    
    domain_ids = user_domains.values_list('domain_id', flat=True)
    recent_resources = Resource.objects.filter(
        domain_id__in=domain_ids,
        is_approved=True
    ).select_related('domain', 'uploaded_by').order_by('-created_at')[:5]
    
    
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    weekly_report = WeeklyProgressReport.objects.filter(
        user=user,
        week_start=week_start
    ).first()
    
    
    buddies_count = TechBuddy.objects.filter(
        Q(requester=user, status='accepted') |
        Q(receiver=user, status='accepted')
    ).count()
    
    
    current_recognitions = DomainRecognition.objects.filter(
        user=user,
        week_start__lte=today,
        week_end__gte=today
    ).select_related('domain')
    
    
    total_goals = Goal.objects.filter(user=user).count()
    completed_goals = Goal.objects.filter(user=user, status='completed').count()
    completion_rate = (completed_goals / total_goals * 100) if total_goals > 0 else 0
    
    context = {
        'user': user,
        'user_domains': user_domains,
        'active_goals': active_goals,
        'recent_resources': recent_resources,
        'weekly_report': weekly_report,
        'buddies_count': buddies_count,
        'current_recognitions': current_recognitions,
        'total_goals': total_goals,
        'completed_goals': completed_goals,
        'completion_rate': completion_rate,
    }
    
    return render(request, 'dashboard/home.html', context)
