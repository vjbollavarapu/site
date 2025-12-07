from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Lead


@login_required
def lead_list(request):
    """Display list of all leads/prospects"""
    leads = Lead.objects.all()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        leads = leads.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(company__icontains=search_query)
        )
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        leads = leads.filter(status=status_filter)
    
    # Filter by lifecycle stage
    stage_filter = request.GET.get('stage', '')
    if stage_filter:
        leads = leads.filter(lifecycle_stage=stage_filter)
    
    # Pagination
    paginator = Paginator(leads, 25)  # Show 25 leads per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'stage_filter': stage_filter,
        'status_choices': Lead.STATUS_CHOICES,
        'stage_choices': Lead.LIFECYCLE_STAGE_CHOICES,
    }
    
    return render(request, 'leads/lead_list.html', context)


@login_required
def lead_detail(request, pk):
    """Display detailed view of a single lead"""
    lead = Lead.objects.get(pk=pk)
    context = {
        'lead': lead,
    }
    return render(request, 'leads/lead_detail.html', context)
