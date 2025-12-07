"""
GDPR API views
"""
import secrets
import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from django_ratelimit.core import is_ratelimited
from django.utils import timezone

from .models import Consent, PrivacyPolicy, DataRetentionPolicy, DataDeletionAudit
from .serializers import (
    ConsentSerializer, ConsentCreateSerializer, PrivacyPolicySerializer,
    DataExportSerializer, DataDeletionSerializer, DataRetentionPolicySerializer
)
from .services import GDPRService
from apps.analytics.utils import get_client_ip, hash_ip_address

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])
def manage_consent(request):
    """
    POST /api/gdpr/consent/
    Accept or withdraw consent
    Rate limited: 10 requests per IP per hour
    """
    # Rate limiting
    if is_ratelimited(request, group='gdpr-consent', key='ip', rate='10/h', method='POST', increment=True):
        return Response(
            {'error': 'Too many requests. Please try again later.'},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )
    
    serializer = ConsentCreateSerializer(data=request.data)
    
    if serializer.is_valid():
        email = serializer.validated_data['email'].lower().strip()
        consent_type = serializer.validated_data['consent_type']
        consent_given = serializer.validated_data['consent_given']
        
        # Get privacy policy if version specified
        privacy_policy = None
        if serializer.validated_data.get('privacy_policy_version'):
            try:
                privacy_policy = PrivacyPolicy.objects.get(
                    version=serializer.validated_data['privacy_policy_version'],
                    is_active=True
                )
            except PrivacyPolicy.DoesNotExist:
                # Use current active policy
                privacy_policy = PrivacyPolicy.objects.filter(is_active=True).first()
        else:
            # Use current active policy
            privacy_policy = PrivacyPolicy.objects.filter(is_active=True).first()
        
        # Get IP and hash it
        ip_address = get_client_ip(request)
        ip_hash = Consent.hash_ip_address(ip_address) if ip_address else None
        
        # Create consent record
        consent = Consent.objects.create(
            email=email,
            consent_type=consent_type,
            consent_given=consent_given,
            consent_timestamp=timezone.now() if consent_given else None,
            withdrawal_timestamp=timezone.now() if not consent_given else None,
            consent_text=serializer.validated_data.get('consent_text', ''),
            privacy_policy=privacy_policy,
            ip_address_hash=ip_hash,
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            source=serializer.validated_data.get('source', ''),
        )
        
        return Response({
            'success': True,
            'message': 'Consent recorded successfully',
            'consent': ConsentSerializer(consent).data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def export_user_data(request, email):
    """
    GET /api/gdpr/export/{email}/
    Export all user data in JSON format
    Rate limited: 5 requests per IP per hour
    """
    # Rate limiting
    if is_ratelimited(request, group='gdpr-export', key='ip', rate='5/h', method='GET', increment=True):
        return Response(
            {'error': 'Too many requests. Please try again later.'},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )
    
    try:
        # Export user data
        data = GDPRService.export_user_data(email)
        
        return Response(data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error exporting user data: {str(e)}")
        return Response(
            {'error': 'Failed to export user data'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def access_user_data(request, email):
    """
    GET /api/gdpr/access/{email}/
    Right to Access - Return all data associated with email
    Rate limited: 5 requests per IP per hour
    """
    # Rate limiting
    if is_ratelimited(request, group='gdpr-access', key='ip', rate='5/h', method='GET', increment=True):
        return Response(
            {'error': 'Too many requests. Please try again later.'},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )
    
    try:
        # Get user data (same as export)
        data = GDPRService.get_user_data(email)
        
        return Response(data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error accessing user data: {str(e)}")
        return Response(
            {'error': 'Failed to access user data'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE', 'POST'])
@permission_classes([AllowAny])
def delete_user_data(request, email):
    """
    DELETE /api/gdpr/delete/{email}/
    Delete or anonymize all user data
    Requires confirmation
    Rate limited: 3 requests per IP per hour
    """
    # Rate limiting
    if is_ratelimited(request, group='gdpr-delete', key='ip', rate='3/h', method='DELETE', increment=True):
        return Response(
            {'error': 'Too many requests. Please try again later.'},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )
    
    # For POST requests, get data from body
    if request.method == 'POST':
        serializer = DataDeletionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        anonymize = serializer.validated_data.get('anonymize', False)
        confirmation = serializer.validated_data.get('confirmation', False)
        confirmation_token = serializer.validated_data.get('confirmation_token', '')
    else:
        # For DELETE, check query params
        anonymize = request.query_params.get('anonymize', 'false').lower() == 'true'
        confirmation = request.query_params.get('confirmation', 'false').lower() == 'true'
        confirmation_token = request.query_params.get('confirmation_token', '')
    
    # Require confirmation
    if not confirmation:
        # Generate confirmation token for first request
        if not confirmation_token:
            token = secrets.token_urlsafe(32)
            # Store token temporarily (in real app, send via email)
            return Response({
                'error': 'Confirmation required',
                'message': 'Please confirm deletion by including confirmation=true and the confirmation_token',
                'confirmation_token': token,
                'warning': 'This action cannot be undone. All data associated with this email will be deleted.'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Get IP for audit
        ip_address = get_client_ip(request)
        
        # Delete/anonymize user data
        deletion_summary = GDPRService.delete_user_data(
            email=email,
            anonymize=anonymize,
            keep_audit=True,
            deleted_by='user',
            ip_address=ip_address
        )
        
        return Response({
            'success': True,
            'message': f"Data {'anonymized' if anonymize else 'deleted'} successfully",
            'summary': deletion_summary
        }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error deleting user data: {str(e)}")
        return Response(
            {'error': 'Failed to delete user data'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def list_consents(request):
    """Admin endpoint to list all consents"""
    email = request.query_params.get('email')
    consent_type = request.query_params.get('consent_type')
    
    queryset = Consent.objects.all()
    
    if email:
        queryset = queryset.filter(email__iexact=email)
    if consent_type:
        queryset = queryset.filter(consent_type=consent_type)
    
    serializer = ConsentSerializer(queryset[:100], many=True)  # Limit to 100
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def manage_privacy_policy(request):
    """Admin endpoint to manage privacy policies"""
    if request.method == 'GET':
        policies = PrivacyPolicy.objects.all()
        serializer = PrivacyPolicySerializer(policies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        serializer = PrivacyPolicySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def manage_retention_policies(request):
    """Admin endpoint to manage data retention policies"""
    if request.method == 'GET':
        policies = DataRetentionPolicy.objects.all()
        serializer = DataRetentionPolicySerializer(policies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        serializer = DataRetentionPolicySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def apply_retention_policies(request):
    """Admin endpoint to manually trigger retention policy application"""
    try:
        summary = GDPRService.apply_retention_policies()
        return Response({
            'success': True,
            'message': 'Retention policies applied successfully',
            'summary': summary
        }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error applying retention policies: {str(e)}")
        return Response(
            {'error': 'Failed to apply retention policies'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

