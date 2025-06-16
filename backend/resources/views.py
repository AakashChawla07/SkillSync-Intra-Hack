from sys import stdout
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import timedelta
from .models import Resource, ResourceBookmark
from domains.models import TechDomain

# Create your views here.
@login_required
def resource_list(request):
    resources = Resource.objects.filter(is_approved=True).select_related('domain', 'uploaded_by')
    
    domain_id = request.GET.get('domain')
    selected_domain_obj = None
    if domain_id:
        resources = resources.filter(domain_id=domain_id)
        selected_domain_obj = get_object_or_404(TechDomain, id=domain_id)
    
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
    
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_resources = Resource.objects.filter(
        is_approved=True,
        created_at__gte=thirty_days_ago
    ).select_related('domain', 'uploaded_by').order_by('-created_at')[:8]
    
    featured_resource = Resource.objects.filter(
        is_approved=True
    ).annotate(
        bookmark_count=Count('resourcebookmark')
    ).select_related('domain', 'uploaded_by').order_by('-bookmark_count').first()
    
    default_domain = selected_domain_obj or domains.first()
    domain_resources = []
    
    if default_domain:
        domain_resources = Resource.objects.filter(
            is_approved=True,
            domain=default_domain
        ).select_related('domain', 'uploaded_by').order_by('-created_at')[:4]
    
    resource_type_counts = {}
    for type_code, type_name in Resource.RESOURCE_TYPES:
        count = Resource.objects.filter(
            is_approved=True, 
            resource_type=type_code
        ).count()
        resource_type_counts[type_code] = count
    
    context = {
        'resources': resources.order_by('-created_at'),
        'domains': domains,
        'selected_domain': domain_id,
        'selected_domain_obj': selected_domain_obj,
        'selected_type': resource_type,
        'search_query': search_query,
        'resource_types': Resource.RESOURCE_TYPES,
        'resource_type_counts': resource_type_counts,
        'recent_resources': recent_resources,
        'featured_resource': featured_resource,
        'domain_resources': domain_resources,
        'default_domain': default_domain,
        'user': request.user
    }
    
    return render(request, 'resources/resource_list.html', context)

@login_required
def resource_detail(request, resource_id):
    resource = get_object_or_404(Resource, id=resource_id, is_approved=True)
    
    is_bookmarked = ResourceBookmark.objects.filter(
        user=request.user, 
        resource=resource
    ).exists()
    # Process tags
    tags = [tag.strip() for tag in resource.tags.split(',') if tag.strip()] if resource.tags else []
    
    related_resources = Resource.objects.filter(
        domain=resource.domain,
        is_approved=True
    ).exclude(id=resource.id).select_related('domain', 'uploaded_by')[:4]
    
    # Get bookmark count for this resource
    bookmark_count = ResourceBookmark.objects.filter(resource=resource).count()
    
    context = {
        'resource': resource,
        'is_bookmarked': is_bookmarked,
        'tags': tags,
        'related_resources': related_resources,
        'bookmark_count': bookmark_count,
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
        
        # Validate required fields
        if not all([title, description, resource_type, domain_id]):
            messages.error(request, 'Please fill in all required fields.')
            domains = TechDomain.objects.filter(is_active=True)
            return render(request, 'resources/upload_resource.html', {
                'domains': domains,
                'resource_types': Resource.RESOURCE_TYPES
            })
        
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
        
        messages.success(request, 'Resource uploaded successfully and is pending approval!')
        return redirect('resource_list')
    
    domains = TechDomain.objects.filter(is_active=True)
    
    return render(request, 'resources/upload_resource.html', {
        'domains': domains,
        'resource_types': Resource.RESOURCE_TYPES
    })

@login_required
def toggle_bookmark(request, resource_id):
    if request.method == 'POST':
        resource = get_object_or_404(Resource, id=resource_id, is_approved=True)
        bookmark, created = ResourceBookmark.objects.get_or_create(
            user=request.user,
            resource=resource
        )

        if not created:
            bookmark.delete()
            message = 'Resource removed from bookmarks'
        else:
            message = 'Resource bookmarked successfully'

        messages.success(request, message)
        return redirect('resource_detail', resource_id=resource_id)

    return redirect('resource_list')

@login_required
@login_required
def resources_by_domain(request, domain_id):
    domain = get_object_or_404(TechDomain, id=domain_id)
    resources = Resource.objects.filter(
        is_approved=True,
        domain=domain
    ).select_related('domain', 'uploaded_by').order_by('-created_at')[:4]

    return render(request, 'resources/domain_resources.html', {
        'resources': resources,
        'domain': domain
    })

@login_required
def filter_resources(request):
    category = request.GET.get('category', 'all')
    domain_id = request.GET.get('domain')
    search_query = request.GET.get('search')

    resources = Resource.objects.filter(is_approved=True).select_related('domain', 'uploaded_by')

    if category != 'all':
        category_mapping = {
            'tutorials': 'tutorial',
            'documentation': 'document',
            'courses': 'course',
            'videos': 'video',
            'tools': 'tool',
            'books': 'book',
        }
        if category in category_mapping:
            resources = resources.filter(resource_type=category_mapping[category])

    if domain_id:
        resources = resources.filter(domain_id=domain_id)

    if search_query:
        resources = resources.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(tags__icontains=search_query)
        )

    resources = resources.order_by('-created_at')

    return render(request, 'resources/resource_list.html', {
        'resources': resources[:12],
        'count': resources.count(),
        'selected_category': category,
        'selected_domain': domain_id,
        'search_query': search_query,
    })