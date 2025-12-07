from rest_framework import viewsets, status, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.utils import timezone
from django.db.models import Count, Q
from django.utils.dateparse import parse_date
from django_ratelimit.core import is_ratelimited
from drf_spectacular.utils import extend_schema, OpenApiResponse
from drf_spectacular.types import OpenApiTypes
import logging
from .models import WaitlistEntry
from apps.integrations.email_service import email_service
from apps.integrations.crm_service import crm_service

logger = logging.getLogger(__name__)
from .serializers import (
    WaitlistJoinSerializer,
    WaitlistVerifySerializer,
    WaitlistEntrySerializer,
    WaitlistEntryUpdateSerializer,
    WaitlistStatusSerializer
)


@extend_schema(
    request=WaitlistJoinSerializer,
    responses={
        201: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description='Successfully joined waitlist'
        ),
        400: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description='Validation error'
        ),
        429: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description='Rate limit exceeded'
        ),
    },
    tags=['Waitlist'],
    summary='Join waitlist',
    description='Public endpoint to join waitlist. Creates entry and sends verification email. Rate limited: 5 requests per IP per hour.'
)
@api_view(['POST'])
@permission_classes([AllowAny])
def join_waitlist(request):
    """
    Public endpoint to join waitlist
    Creates entry and sends verification email
    Rate limited: 5 requests per IP per hour
    """
    # Rate limiting check
    if is_ratelimited(request, group='waitlist-join', key='ip', rate='5/h', method='POST', increment=True):
        return Response(
            {'error': 'Too many requests. Please try again later.'},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )
    
    serializer = WaitlistJoinSerializer(data=request.data)
    
    if serializer.is_valid():
        # Extract metadata
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        referrer = request.META.get('HTTP_REFERER', '')
        
        # Get A/B test info
        ab_test_name = serializer.validated_data.pop('ab_test_name', None)
        ab_test_variant = None
        
        # If A/B test name provided, get or assign variant
        if ab_test_name:
            try:
                from apps.ab_testing.services import ABTestingService
                user_identifier = serializer.validated_data.get('email') or request.session.session_key or 'anonymous'
                ab_test_variant = ABTestingService.get_variant(ab_test_name, user_identifier)
            except Exception as e:
                logger.error(f"Failed to get A/B test variant: {e}")
                ab_test_name = None
        
        # Generate verification token
        import secrets
        verification_token = secrets.token_urlsafe(32)
        
        # Create waitlist entry
        entry = WaitlistEntry.objects.create(
            **serializer.validated_data,
            ab_test_name=ab_test_name,
            ab_test_variant=ab_test_variant,
            marketing_consent=True,  # Assuming consent given if form submitted
            consent_timestamp=timezone.now(),
            verification_token=verification_token
        )
        
        # Calculate priority score
        entry.calculate_priority_score()
        entry.save()
        
        # Send verification email using email service
        try:
            email_service.send_waitlist_verification(entry)
        except Exception as e:
            # Log error but don't fail the request
            logger.error(f"Failed to send verification email: {e}")
        
        # Sync to CRM
        try:
            crm_service.sync_waitlist_entry(entry)
        except Exception as e:
            logger.error(f"Failed to sync waitlist to CRM: {e}")
        
        # Track A/B test conversion
        if ab_test_name and ab_test_variant:
            try:
                from apps.ab_testing.services import ab_testing_service
                user_identifier = entry.email or request.session.session_key or 'anonymous'
                ab_testing_service.track_conversion(
                    ab_test_name,
                    user_identifier,
                    entry,
                    conversion_type='waitlist_join'
                )
            except Exception as e:
                logger.error(f"Failed to track A/B test conversion: {e}")
        
        # Send webhook
        try:
            from apps.webhooks.services import webhook_service
            webhook_service.send_webhook(
                'waitlist_join',
                {
                    'id': str(entry.id),
                    'email': entry.email,
                    'name': entry.name,
                    'company': entry.company,
                    'status': entry.status,
                    'priority_score': entry.priority_score,
                    'ab_test_variant': ab_test_variant,
                    'created_at': entry.created_at.isoformat(),
                },
                entity_id=str(entry.id)
            )
        except Exception as e:
            logger.error(f"Failed to send webhook: {e}")
        
        return Response({
            'success': True,
            'message': 'Thank you for joining! Please check your email to verify your address.',
            'entry_id': str(entry.id)
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    request=WaitlistVerifySerializer,
    responses={
        200: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description='Email verified successfully'
        ),
        400: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description='Validation error'
        ),
    },
    tags=['Waitlist'],
    summary='Verify waitlist email',
    description='Public endpoint to verify email address using verification token.'
)
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_waitlist_email(request):
    """
    Public endpoint to verify email address
    """
    serializer = WaitlistVerifySerializer(data=request.data)
    
    if serializer.is_valid():
        token = serializer.validated_data['token']
        
        try:
            entry = WaitlistEntry.objects.get(verification_token=token)
            entry.verify()
            
            return Response({
                'success': True,
                'message': 'Email verified successfully!'
            }, status=status.HTTP_200_OK)
        except WaitlistEntry.DoesNotExist:
            return Response({
                'error': 'Invalid verification token.'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    responses={
        200: WaitlistStatusSerializer,
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description='Email not found in waitlist'
        ),
    },
    tags=['Waitlist'],
    summary='Check waitlist status',
    description='Public endpoint to check waitlist status for an email address.'
)
@api_view(['GET'])
@permission_classes([AllowAny])
def check_waitlist_status(request, email):
    """
    Public endpoint to check waitlist status by email
    """
    # Decode URL-encoded email if needed
    from urllib.parse import unquote
    email = unquote(email).lower().strip()
    
    try:
        entry = WaitlistEntry.objects.get(email=email)
        
        # Calculate position (entries with higher priority_score or earlier created_at)
        position = WaitlistEntry.objects.filter(
            Q(priority_score__gt=entry.priority_score) |
            (Q(priority_score=entry.priority_score) & Q(created_at__lt=entry.created_at))
        ).count() + 1
        
        return Response({
            'email': entry.email,
            'status': entry.status,
            'is_verified': entry.is_verified,
            'position': position,
            'priority_score': entry.priority_score,
            'created_at': entry.created_at
        }, status=status.HTTP_200_OK)
    except WaitlistEntry.DoesNotExist:
        return Response({
            'error': 'Email not found on waitlist.'
        }, status=status.HTTP_404_NOT_FOUND)


class WaitlistEntryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing waitlist entries (admin only)
    """
    queryset = WaitlistEntry.objects.all()
    serializer_class = WaitlistEntrySerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['email', 'name', 'company', 'role']
    ordering_fields = ['created_at', 'priority_score', 'status']
    ordering = ['-priority_score', '-created_at']
    
    def get_queryset(self):
        """Filter queryset based on query parameters"""
        queryset = WaitlistEntry.objects.all()
        
        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by industry
        industry_filter = self.request.query_params.get('industry', None)
        if industry_filter:
            queryset = queryset.filter(industry=industry_filter)
        
        # Filter by company size
        company_size_filter = self.request.query_params.get('company_size', None)
        if company_size_filter:
            queryset = queryset.filter(company_size=company_size_filter)
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from', None)
        date_to = self.request.query_params.get('date_to', None)
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        return queryset
    
    def update(self, request, *args, **kwargs):
        """Update waitlist entry"""
        instance = self.get_object()
        serializer = WaitlistEntryUpdateSerializer(instance, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(WaitlistEntrySerializer(instance).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def invite(self, request, pk=None):
        """Send invitation email to waitlist entry"""
        entry = self.get_object()
        
        # Generate invite code and send invitation
        invite_code = entry.send_invitation(user=request.user)
        
        # Send invitation email using email service
        try:
            email_service.send_waitlist_invitation(entry)
        except Exception as e:
            # Log error but don't fail the request
            logger.error(f"Failed to send invitation email: {e}")
        
        return Response({
            'success': True,
            'message': f'Invitation sent to {entry.email}',
            'invite_code': invite_code
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get waitlist statistics for dashboard"""
        queryset = self.get_queryset()
        
        # Total entries
        total_entries = queryset.count()
        
        # By status
        by_status = queryset.values('status').annotate(count=Count('id')).order_by('status')
        status_dict = {item['status']: item['count'] for item in by_status}
        
        # By industry
        by_industry = queryset.values('industry').annotate(count=Count('id')).order_by('-count')
        industry_dict = {item['industry'] or 'Unknown': item['count'] for item in by_industry}
        
        # By company size
        by_company_size = queryset.values('company_size').annotate(count=Count('id')).order_by('-count')
        company_size_dict = {item['company_size'] or 'Unknown': item['count'] for item in by_company_size}
        
        # Growth over time (last 30 days)
        from datetime import timedelta
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_entries = queryset.filter(created_at__gte=thirty_days_ago)
        
        # Daily growth
        daily_growth = recent_entries.extra(
            select={'day': "date(created_at)"}
        ).values('day').annotate(count=Count('id')).order_by('day')
        
        return Response({
            'total_entries': total_entries,
            'by_status': status_dict,
            'by_industry': industry_dict,
            'by_company_size': company_size_dict,
            'growth_last_30_days': recent_entries.count(),
            'daily_growth': list(daily_growth)
        }, status=status.HTTP_200_OK)


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# Email sending functions moved to email_service

