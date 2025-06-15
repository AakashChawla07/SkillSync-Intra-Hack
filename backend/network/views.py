
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import TechBuddy
from accounts.models import User
from domains.models import TechDomain, UserDomain
# Create your views here.

@login_required
def network_dashboard(request):
    accepted_buddies = TechBuddy.objects.filter(
        Q(requester=request.user, status='accepted') | Q(receiver=request.user, status='accepted')
    ).select_related('requester', 'receiver')
    
    pending_requests = TechBuddy.objects.filter(
        receiver=request.user, 
        status='pending'
    ).select_related('requester')
    
    context = {
        'accepted_buddies': accepted_buddies,
        'pending_requests': pending_requests,
        
    }
    
    return render(request, 'network/dashboard.html', context)

@login_required
def find_peers(request):
    user_domains = UserDomain.objects.filter(
        user=request.user, 
        is_active=True
    ).values_list('domain_id', flat=True)
    
    peers = User.objects.filter(
        userdomain__domain_id__in=user_domains,
        userdomain__is_active=True
    ).exclude(id=request.user.id).distinct().select_related()
    
    domain_id = request.GET.get('domain')
    if domain_id:
        peers = peers.filter(userdomain__domain_id=domain_id)
    
    domains = TechDomain.objects.filter(id__in=user_domains)
    
    context = {
        'peers': peers,
        'domains': domains,
        'selected_domain': domain_id,
    }
    
    return render(request, 'network/find_peers.html', context)

@login_required
def send_buddy_request(request, user_id):
    receiver = get_object_or_404(User, id=user_id)
    
    if request.user == receiver:
        messages.error(request, "You cannot send a buddy request to yourself.")
        return redirect('find_peers')
    
    existing_request = TechBuddy.objects.filter(
        Q(requester=request.user, receiver=receiver) |
        Q(requester=receiver, receiver=request.user)
    ).first()
    
    if existing_request:
        messages.warning(request, "A buddy request already exists between you and this user.")
        return redirect('find_peers')
    
    if request.method == 'POST':
        message = request.POST.get('message', '')
        buddy_request = TechBuddy.objects.create(
            requester=request.user,
            receiver=receiver,
            message=message
        )
        
        messages.success(request, f"Buddy request sent to {receiver.get_full_name() or receiver.username}!")
        return redirect('network_dashboard')
    
    return render(request, 'network/send_buddy_request.html', {'receiver': receiver})


@login_required
def respond_request(request, request_id, action):
    techbuddy_request = get_object_or_404(TechBuddy, id=request_id, receiver=request.user)

    if request.method == 'POST':
        if action == 'accept':
            techbuddy_request.status = 'accepted'
            techbuddy_request.save()
        elif action == 'reject':
            techbuddy_request.status = 'declined'
            techbuddy_request.delete()

    return redirect('network_dashboard')