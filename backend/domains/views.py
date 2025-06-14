
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count,Q
from .models import TechDomain, UserDomain, DomainRecognition
from resources.models import Resource

# Create your views here.
@login_required
def domain_list(request):
    domains = TechDomain.objects.filter(is_active=True).annotate(
        member_count=Count('userdomain', filter=Q(userdomain__is_active=True))
    )
    user_domains = UserDomain.objects.filter(user=request.user, is_active=True).values_list('domain_id', flat=True)
    
    return render(request, 'domains/domain_list.html', {
        'domains': domains,
        'user_domains': user_domains
    })

@login_required
def domain_detail(request, domain_id):
    domain = get_object_or_404(TechDomain, id=domain_id, is_active=True)
    
    members = UserDomain.objects.filter(domain=domain, is_active=True).select_related('user')
    
    resources = Resource.objects.filter(domain=domain, is_approved=True).order_by('-created_at')[:10]
    
    from datetime import date, timedelta
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    recognitions = DomainRecognition.objects.filter(
        domain=domain, 
        week_start__lte=today, 
        week_end__gte=today
    ).select_related('user')
    
    is_member = UserDomain.objects.filter(user=request.user, domain=domain, is_active=True).exists()
    
    context = {
        'domain': domain,
        'members': members,
        'resources': resources,
        'recognitions': recognitions,
        'is_member': is_member,
    }
    
    return render(request, 'domains/domain_detail.html', context)

@login_required
def join_domain(request, domain_id):
    domain = get_object_or_404(TechDomain, id=domain_id, is_active=True)
    
    if request.method == 'POST':
        skill_level = request.POST.get('skill_level')
        goals = request.POST.get('goals', '')
        
        user_domain, created = UserDomain.objects.get_or_create(
            user=request.user,
            domain=domain,
            defaults={
                'skill_level': skill_level,
                'goals': goals,
                'is_active': True
            }
        )
        
        if not created:
            user_domain.is_active = True
            user_domain.skill_level = skill_level
            user_domain.goals = goals
            user_domain.save()
            messages.success(request, f'Successfully rejoined {domain.name}!')
        else:
            messages.success(request, f'Successfully joined {domain.name}!')
        
        return redirect('domain_detail', domain_id=domain.id)
    
    return render(request, 'domains/join_domain.html', {'domain': domain})

