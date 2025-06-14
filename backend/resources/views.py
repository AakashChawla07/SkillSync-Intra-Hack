
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Resource, ResourceBookmark
from domains.models import TechDomain

# Create your views here.
@login_required
def resource_list(request):
    resources = Resource.objects.filter(is_approved=True).select_related('domain', 'uploaded_by')
    
    domain_id = request.GET.get('domain')
    if domain_id:
        resources = resources.filter(domain_id=domain_id)
    
    resource_type = request.GET.get('type')
    if resource_type:
        resources = resources.filter(resource_type=resource_type)
    
    search_query = request.GET.get('search')
    if search_query:
        resources = resources.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(tags__icontains=search_query)
        )
    
    domains = TechDomain.objects.filter(is_active=True)
    
    context = {
        'resources': resources.order_by('-created_at'),
        'domains': domains,
        'selected_domain': domain_id,
        'selected_type': resource_type,
        'search_query': search_query,
        'resource_types': Resource.RESOURCE_TYPES,
        'user':request.user
    }
    
    return render(request, 'resources/resource_list.html', context)

@login_required
def resource_detail(request, resource_id):
    resource = get_object_or_404(Resource, id=resource_id, is_approved=True)
    
    is_bookmarked = ResourceBookmark.objects.filter(user=request.user, resource=resource).exists()

    tags = resource.tags.split(',') if resource.tags else []
    context = {
        'resource': resource,
        'is_bookmarked': is_bookmarked,
        'tags':tags
    }
    
    return render(request, 'resources/resource_detail.html', context)

@login_required
def upload_resource(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        resource_type = request.POST.get('resource_type')
        domain_id = request.POST.get('domain')
        url = request.POST.get('url', '')
        tags = request.POST.get('tags', '')
        file = request.FILES.get('file')
        
        domain = get_object_or_404(TechDomain, id=domain_id)
        
        resource = Resource.objects.create(
            title=title,
            description=description,
            resource_type=resource_type,
            domain=domain,
            uploaded_by=request.user,
            url=url,
            file=file,
            tags=tags,
        )
        
        messages.success(request, 'Resource uploaded successfully!')
        return redirect('resource_list')
    
    domains = TechDomain.objects.filter(is_active=True)
    
    return render(request, 'resources/upload_resource.html', {
        'domains': domains,
        'resource_types': Resource.RESOURCE_TYPES
    })
