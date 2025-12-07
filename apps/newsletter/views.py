from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from .models import NewsletterSubscription


@login_required
def newsletter_list(request):
    """Display list of all newsletter subscriptions"""
    subscriptions = NewsletterSubscription.objects.all()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        subscriptions = subscriptions.filter(
            Q(email__icontains=search_query) |
            Q(name__icontains=search_query)
        )
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        subscriptions = subscriptions.filter(subscription_status=status_filter)
    
    # Filter by source
    source_filter = request.GET.get('source', '')
    if source_filter:
        subscriptions = subscriptions.filter(source=source_filter)
    
    # Filter by preference
    preference_filter = request.GET.get('preference', '')
    if preference_filter:
        subscriptions = subscriptions.filter(preference=preference_filter)
    
    # Filter verified/unverified
    verified_filter = request.GET.get('verified', '')
    if verified_filter == 'yes':
        subscriptions = subscriptions.filter(is_verified=True)
    elif verified_filter == 'no':
        subscriptions = subscriptions.filter(is_verified=False)
    
    # Sort by date (default)
    sort_by = request.GET.get('sort', 'date')
    if sort_by == 'email':
        subscriptions = subscriptions.order_by('email')
    else:
        subscriptions = subscriptions.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(subscriptions, 25)  # Show 25 subscriptions per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'source_filter': source_filter,
        'preference_filter': preference_filter,
        'verified_filter': verified_filter,
        'sort': sort_by,
        'status_choices': NewsletterSubscription.STATUS_CHOICES,
        'source_choices': NewsletterSubscription.SOURCE_CHOICES,
        'preference_choices': NewsletterSubscription.PREFERENCE_CHOICES,
    }
    
    return render(request, 'newsletter/newsletter_list.html', context)


@login_required
def newsletter_detail(request, pk):
    """Display detailed view of a single newsletter subscription"""
    subscription = NewsletterSubscription.objects.get(pk=pk)
    context = {
        'subscription': subscription,
    }
    return render(request, 'newsletter/newsletter_detail.html', context)

