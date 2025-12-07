from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.http import Http404
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes, throttle_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from django_ratelimit.core import is_ratelimited
from django.conf import settings
from .models import ContactSubmission
from .serializers import (
    ContactSubmissionCreateSerializer,
    ContactSubmissionSerializer,
    ContactSubmissionUpdateSerializer
)
from .security import detect_spam, verify_recaptcha
from .services import CheckSubmissionSpam
from apps.integrations.email_service import email_service
from apps.integrations.crm_service import crm_service
from apps.integrations.i18n_utils import get_user_language, activate_language


class ContactSubmissionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing contact submissions (admin only)
    """
    queryset = ContactSubmission.objects.all()
    serializer_class = ContactSubmissionSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'email', 'subject', 'message', 'company']
    ordering_fields = ['created_at', 'updated_at', 'priority', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter queryset based on query parameters"""
        queryset = ContactSubmission.objects.all()
        
        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by priority
        priority_filter = self.request.query_params.get('priority', None)
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from', None)
        date_to = self.request.query_params.get('date_to', None)
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        # Filter out spam by default (unless explicitly requested)
        exclude_spam = self.request.query_params.get('include_spam', 'false').lower() != 'true'
        if exclude_spam:
            queryset = queryset.filter(is_spam=False)
        
        return queryset
    
    def destroy(self, request, *args, **kwargs):
        """Soft delete - archive instead of delete"""
        instance = self.get_object()
        instance.status = 'archived'
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """Update status of contact submission"""
        submission = self.get_object()
        serializer = ContactSubmissionUpdateSerializer(submission, data=request.data, partial=True)
        
        if serializer.is_valid():
            # Handle status changes
            new_status = serializer.validated_data.get('status')
            if new_status:
                if new_status == 'contacted' and not submission.contacted_at:
                    submission.contacted_at = timezone.now()
                elif new_status == 'resolved' and not submission.resolved_at:
                    submission.resolved_at = timezone.now()
            
            serializer.save()
            return Response(ContactSubmissionSerializer(submission).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def submit_contact_form(request):
    """
    Submit a contact form.
    
    Public endpoint for submitting contact forms. Includes spam detection,
    email confirmation, and optional CRM integration.
    
    **Rate Limit:** 5 submissions per IP per hour
    
    **Authentication:** Not required (public endpoint)
    
    **Request Body:**
    - name (required): Contact name
    - email (required): Contact email
    - subject (required): Message subject
    - message (required): Message content (min 10, max 10000 characters)
    - phone (optional): Contact phone number
    - company (optional): Company name
    - source (optional): Source URL
    - referrer (optional): Referrer URL
    
    **Response:**
    - 201 Created: Submission successful
    - 400 Bad Request: Validation errors
    - 429 Too Many Requests: Rate limit exceeded
    
    **Example Request:**
    ```json
    {
        "name": "John Doe",
        "email": "john@example.com",
        "subject": "Inquiry about services",
        "message": "I would like to know more about your services.",
        "phone": "+1234567890",
        "company": "Example Corp"
    }
    ```
    
    **Example Response:**
    ```json
    {
        "success": true,
        "submission_id": "uuid-here",
        "message": "Thank you for your submission. We will contact you soon."
    }
    ```
    """
    # Rate limiting check
    if is_ratelimited(request, group='contact-submit', key='ip', rate='5/h', method='POST', increment=True):
        return Response(
            {'error': 'Too many submissions. Please try again later.'},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )
    
    # Detect and activate user language
    user_language = get_user_language(request)
    activate_language(user_language)
    
    serializer = ContactSubmissionCreateSerializer(data=request.data)
    
    if serializer.is_valid():
        # Extract honeypot and reCAPTCHA token (remove from validated_data)
        honeypot_value = serializer.validated_data.pop('website', '')
        recaptcha_token = serializer.validated_data.pop('recaptcha_token', '')
        
        # Verify honeypot
        if honeypot_value and honeypot_value.strip():
            return Response(
                {'error': 'Spam detected.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify reCAPTCHA if enabled
        recaptcha_secret = getattr(settings, 'RECAPTCHA_SECRET_KEY', None)
        if recaptcha_secret:
            success, score, error = verify_recaptcha(recaptcha_token, recaptcha_secret)
            if not success:
                return Response(
                    {'error': f'reCAPTCHA verification failed: {error}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if score < 0.5:  # Threshold for reCAPTCHA v3
                # Log low score for review but allow submission
                print(f"Low reCAPTCHA score: {score} for IP: {get_client_ip(request)}")
        
        # Extract IP address and user agent
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        referrer = request.META.get('HTTP_REFERER', '')
        
        # Enhanced spam detection using service
        spam_checker = CheckSubmissionSpam(serializer.validated_data, request)
        is_spam, spam_score, spam_reasons, spam_logs = spam_checker.calculate_spam_score(
            honeypot_value=honeypot_value,
            recaptcha_token=recaptcha_token
        )
        
        # Create submission
        submission = ContactSubmission.objects.create(
            **serializer.validated_data,
            ip_address=ip_address,
            user_agent=user_agent,
            referrer=referrer,
            spam_score=spam_score,
            is_spam=is_spam,
            ab_test_name=ab_test_name,
            ab_test_variant=ab_test_variant,
            consent_given=True,  # Assuming consent given if form submitted
            consent_timestamp=timezone.now() if not is_spam else None
        )
        
        # Send confirmation email (only if not spam)
        if not is_spam:
            try:
                email_service.send_contact_confirmation(submission)
            except Exception as e:
                logger.error(f"Failed to send confirmation email: {e}")
        
        # Sync to CRM (only if not spam and CRM configured)
        if not is_spam:
            try:
                crm_service.sync_contact_submission(submission)
            except Exception as e:
                logger.error(f"Failed to sync to CRM: {e}")
            
            # Track A/B test conversion
            if ab_test_name and ab_test_variant:
                try:
                    from apps.ab_testing.services import ab_testing_service
                    user_identifier = submission.email or request.session.session_key or 'anonymous'
                    ab_testing_service.track_conversion(
                        ab_test_name,
                        user_identifier,
                        submission,
                        conversion_type='contact_submission'
                    )
                except Exception as e:
                    logger.error(f"Failed to track A/B test conversion: {e}")
            
            # Send webhook (only if not spam)
            try:
                from apps.webhooks.services import webhook_service
                webhook_service.send_webhook(
                    'contact_submission',
                    {
                        'id': str(submission.id),
                        'name': submission.name,
                        'email': submission.email,
                        'subject': submission.subject,
                        'status': submission.status,
                        'priority': submission.priority,
                        'ab_test_variant': ab_test_variant,
                        'created_at': submission.created_at.isoformat(),
                    },
                    entity_id=str(submission.id)
                )
            except Exception as e:
                logger.error(f"Failed to send webhook: {e}")
        
        # Return success response
        return Response({
            'success': True,
            'message': 'Thank you for your submission. We will get back to you soon.',
            'submission_id': str(submission.id)
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# calculate_spam_score function moved to security.py as detect_spam


# Keep the existing Django views for the frontend
@login_required
def contact_list(request):
    """Display list of all contact submissions"""
    contacts = ContactSubmission.objects.filter(is_spam=False)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        contacts = contacts.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(subject__icontains=search_query) |
            Q(company__icontains=search_query)
        )
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        contacts = contacts.filter(status=status_filter)
    
    # Filter by priority
    priority_filter = request.GET.get('priority', '')
    if priority_filter:
        contacts = contacts.filter(priority=priority_filter)
    
    # Pagination
    paginator = Paginator(contacts, 25)  # Show 25 contacts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'status_choices': ContactSubmission.STATUS_CHOICES,
        'priority_choices': ContactSubmission.PRIORITY_CHOICES,
    }
    
    return render(request, 'contacts/contact_list.html', context)


@login_required
def contact_detail(request, pk):
    """Display detailed view of a single contact submission"""
    contact = ContactSubmission.objects.get(pk=pk)
    context = {
        'contact': contact,
    }
    return render(request, 'contacts/contact_detail.html', context)
