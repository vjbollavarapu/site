from rest_framework import viewsets, status, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.utils import timezone
from django.http import HttpResponse
from django.db.models import Count, Q
from django.conf import settings
import csv
import logging
from datetime import timedelta
from .models import NewsletterSubscription
from apps.integrations.email_service import email_service

logger = logging.getLogger(__name__)
from .serializers import (
    NewsletterSubscribeSerializer,
    NewsletterVerifySerializer,
    NewsletterUnsubscribeSerializer,
    NewsletterSubscriptionSerializer
)


@api_view(['POST'])
@permission_classes([AllowAny])
def subscribe_newsletter(request):
    """
    Public endpoint to subscribe to newsletter
    Implements double opt-in flow
    """
    serializer = NewsletterSubscribeSerializer(data=request.data)
    
    if serializer.is_valid():
        email = serializer.validated_data['email'].lower().strip()
        
        # Check if already exists (for resubscription)
        existing = NewsletterSubscription.objects.filter(email=email).first()
        
        if existing:
            # Resubscribe if previously unsubscribed
            if existing.subscription_status == 'unsubscribed':
                existing.subscription_status = 'subscribed'
                existing.consent_given = True
                existing.consent_timestamp = timezone.now()
                # Update other fields
                for key, value in serializer.validated_data.items():
                    if value:
                        setattr(existing, key, value)
                existing.save()
                subscription = existing
            else:
                # Already subscribed
                return Response({
                    'success': True,
                    'message': 'You are already subscribed to our newsletter.'
                }, status=status.HTTP_200_OK)
        else:
            # Create new subscription
            subscription = NewsletterSubscription.objects.create(
                **serializer.validated_data,
                subscription_status='subscribed',  # Will be verified via email
                consent_given=True,
                consent_timestamp=timezone.now(),
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                referrer=request.META.get('HTTP_REFERER', '')
            )
        
        # Send verification email using email service
        try:
            email_service.send_newsletter_verification(subscription)
        except Exception as e:
            # Log error but don't fail the request
            logger.error(f"Failed to send verification email: {e}")
        
        return Response({
            'success': True,
            'message': 'Please check your email to verify your subscription.'
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_newsletter_subscription(request):
    """
    Public endpoint to verify newsletter subscription
    Completes double opt-in flow
    """
    serializer = NewsletterVerifySerializer(data=request.data)
    
    if serializer.is_valid():
        token = serializer.validated_data['token']
        
        try:
            subscription = NewsletterSubscription.objects.get(verification_token=token)
            subscription.verify()
            
            # Send welcome email after verification
            try:
                email_service.send_newsletter_welcome(subscription)
            except Exception as e:
                logger.error(f"Failed to send welcome email: {e}")
            
            return Response({
                'success': True,
                'message': 'Your subscription has been verified!'
            }, status=status.HTTP_200_OK)
        except NewsletterSubscription.DoesNotExist:
            return Response({
                'error': 'Invalid verification token.'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def unsubscribe_newsletter(request):
    """
    Public endpoint to unsubscribe from newsletter
    Accepts email or token
    """
    serializer = NewsletterUnsubscribeSerializer(data=request.data)
    
    if serializer.is_valid():
        email = serializer.validated_data.get('email', '').strip().lower()
        token = serializer.validated_data.get('token', '').strip()
        reason = serializer.validated_data.get('reason', '')
        
        # Find subscription by email or token
        if email:
            try:
                subscription = NewsletterSubscription.objects.get(email=email)
            except NewsletterSubscription.DoesNotExist:
                return Response({
                    'error': 'Email not found in our subscription list.'
                }, status=status.HTTP_404_NOT_FOUND)
        elif token:
            try:
                subscription = NewsletterSubscription.objects.get(unsubscribe_token=token)
            except NewsletterSubscription.DoesNotExist:
                return Response({
                    'error': 'Invalid unsubscribe token.'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                'error': 'Either email or token must be provided.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Unsubscribe
        subscription.unsubscribe(reason=reason if reason else None)
        
        # Send unsubscribe confirmation
        try:
            email_service.send_newsletter_unsubscribe_confirmation(subscription)
        except Exception as e:
            logger.error(f"Failed to send unsubscribe confirmation: {e}")
        
        return Response({
            'success': True,
            'message': 'You have been successfully unsubscribed from our newsletter.'
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NewsletterSubscriptionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing newsletter subscriptions (admin only)
    """
    queryset = NewsletterSubscription.objects.all()
    serializer_class = NewsletterSubscriptionSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['email', 'name']
    ordering_fields = ['created_at', 'subscription_status', 'preference']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter queryset based on query parameters"""
        queryset = NewsletterSubscription.objects.all()
        
        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(subscription_status=status_filter)
        
        # Filter by interests (if interests is a list in JSONField)
        interests_filter = self.request.query_params.get('interests', None)
        if interests_filter:
            # For JSONField, we need to check if interests array contains the value
            queryset = queryset.filter(interests__contains=[interests_filter])
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from', None)
        date_to = self.request.query_params.get('date_to', None)
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        return queryset
    
    def destroy(self, request, *args, **kwargs):
        """Delete subscriber (GDPR compliance)"""
        instance = self.get_object()
        instance.delete()  # Hard delete for GDPR compliance
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        """Export subscribers to CSV"""
        queryset = self.get_queryset()
        
        # Create HTTP response with CSV header
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="newsletter_subscribers.csv"'
        
        writer = csv.writer(response)
        # Write header
        writer.writerow([
            'Email', 'Name', 'Status', 'Preference', 'Source',
            'Verified', 'Subscribed At', 'Unsubscribed At',
            'Bounce Count', 'Complaint Count'
        ])
        
        # Write data
        for subscription in queryset:
            writer.writerow([
                subscription.email,
                subscription.name or '',
                subscription.subscription_status,
                subscription.preference,
                subscription.source,
                'Yes' if subscription.is_verified else 'No',
                subscription.created_at.strftime('%Y-%m-%d %H:%M:%S') if subscription.created_at else '',
                subscription.unsubscribed_at.strftime('%Y-%m-%d %H:%M:%S') if subscription.unsubscribed_at else '',
                subscription.bounce_count,
                subscription.complaint_count
            ])
        
        return response
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get newsletter statistics"""
        queryset = self.get_queryset()
        
        # Total subscribers
        total_subscribers = queryset.filter(subscription_status='subscribed').count()
        
        # Subscription growth (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_subscriptions = queryset.filter(
            subscription_status='subscribed',
            created_at__gte=thirty_days_ago
        ).count()
        
        # Daily growth (last 30 days)
        daily_growth = queryset.filter(
            subscription_status='subscribed',
            created_at__gte=thirty_days_ago
        ).extra(
            select={'day': "date(created_at)"}
        ).values('day').annotate(count=Count('id')).order_by('day')
        
        # Unsubscribe rate
        total_unsubscribed = queryset.filter(subscription_status='unsubscribed').count()
        total_ever_subscribed = queryset.filter(
            subscription_status__in=['subscribed', 'unsubscribed']
        ).count()
        unsubscribe_rate = (total_unsubscribed / total_ever_subscribed * 100) if total_ever_subscribed > 0 else 0
        
        # Bounce rate
        total_bounced = queryset.filter(subscription_status='bounced').count()
        bounce_rate = (total_bounced / total_subscribers * 100) if total_subscribers > 0 else 0
        
        # By status
        by_status = queryset.values('subscription_status').annotate(count=Count('id')).order_by('subscription_status')
        status_dict = {item['subscription_status']: item['count'] for item in by_status}
        
        # By preference
        by_preference = queryset.filter(subscription_status='subscribed').values('preference').annotate(count=Count('id')).order_by('preference')
        preference_dict = {item['preference']: item['count'] for item in by_preference}
        
        # By source
        by_source = queryset.filter(subscription_status='subscribed').values('source').annotate(count=Count('id')).order_by('-count')
        source_dict = {item['source']: item['count'] for item in by_source}
        
        return Response({
            'total_subscribers': total_subscribers,
            'subscription_growth_last_30_days': recent_subscriptions,
            'daily_growth': list(daily_growth),
            'unsubscribe_rate': round(unsubscribe_rate, 2),
            'bounce_rate': round(bounce_rate, 2),
            'total_unsubscribed': total_unsubscribed,
            'total_bounced': total_bounced,
            'by_status': status_dict,
            'by_preference': preference_dict,
            'by_source': source_dict
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

