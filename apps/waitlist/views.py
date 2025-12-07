from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from .models import WaitlistEntry


@login_required
def waitlist_list(request):
    """Display list of all waitlist entries"""
    entries = WaitlistEntry.objects.all()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        entries = entries.filter(
            Q(email__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(company__icontains=search_query) |
            Q(role__icontains=search_query)
        )
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        entries = entries.filter(status=status_filter)
    
    # Filter by company size
    size_filter = request.GET.get('company_size', '')
    if size_filter:
        entries = entries.filter(company_size=size_filter)
    
    # Filter by industry
    industry_filter = request.GET.get('industry', '')
    if industry_filter:
        entries = entries.filter(industry=industry_filter)
    
    # Sort by priority score (default)
    sort_by = request.GET.get('sort', 'priority')
    if sort_by == 'date':
        entries = entries.order_by('-created_at')
    else:
        entries = entries.order_by('-priority_score', '-created_at')
    
    # Pagination
    paginator = Paginator(entries, 25)  # Show 25 entries per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'size_filter': size_filter,
        'industry_filter': industry_filter,
        'sort': sort_by,
        'status_choices': WaitlistEntry.STATUS_CHOICES,
        'size_choices': WaitlistEntry.COMPANY_SIZE_CHOICES,
        'industry_choices': WaitlistEntry.INDUSTRY_CHOICES,
    }
    
    return render(request, 'waitlist/waitlist_list.html', context)


@login_required
def waitlist_detail(request, pk):
    """Display detailed view of a single waitlist entry"""
    entry = WaitlistEntry.objects.get(pk=pk)
    context = {
        'entry': entry,
    }
    return render(request, 'waitlist/waitlist_detail.html', context)

