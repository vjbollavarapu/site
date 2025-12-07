from rest_framework import viewsets, status, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.utils import timezone
from django.db.models import Count, Q, Avg, Max, Min
from django.contrib.contenttypes.models import ContentType
from .models import Lead
from apps.integrations.crm_service import crm_service
from .serializers import (
    LeadCaptureSerializer,
    LeadTrackEventSerializer,
    LeadSerializer,
    LeadUpdateSerializer,
    LeadDetailSerializer
)
from apps.analytics.models import Event, Conversion


@api_view(['POST'])
@permission_classes([AllowAny])
def capture_lead(request):
    """
    Capture a new lead.
    
    Public endpoint to capture a new lead. Automatically calculates lead score,
    checks for duplicates, and optionally syncs to CRM.
    
    **Rate Limit:** 10 requests per IP per hour
    
    **Authentication:** Not required (public endpoint)
    
    **Request Body:**
    - email (required): Lead email address
    - first_name (required): Lead first name
    - last_name (required): Lead last name
    - phone (optional): Phone number
    - company (optional): Company name
    - job_title (optional): Job title
    - industry (optional): Industry
    - company_size (optional): Company size
    - lead_source (optional): Source of lead (default: 'website')
    
    **Response:**
    - 201 Created: Lead captured successfully
    - 400 Bad Request: Validation errors
    
    **Example Request:**
    ```json
    {
        "email": "lead@example.com",
        "first_name": "Jane",
        "last_name": "Smith",
        "company": "Tech Corp",
        "lead_source": "website"
    }
    ```
    
    **Example Response:**
    ```json
    {
        "success": true,
        "lead_id": "uuid-here",
        "lead_score": 45,
        "message": "Lead captured successfully"
    }
    ```
    """
    serializer = LeadCaptureSerializer(data=request.data)
    
    if serializer.is_valid():
        email = serializer.validated_data['email'].lower().strip()
        
        # Check for duplicate leads
        existing_lead = Lead.objects.filter(email=email).first()
        if existing_lead:
            # Update existing lead if found
            for key, value in serializer.validated_data.items():
                if value:  # Only update non-empty fields
                    setattr(existing_lead, key, value)
            existing_lead.save()
            lead = existing_lead
        else:
            # Create new lead
            lead = Lead.objects.create(
                **serializer.validated_data,
                ab_test_name=ab_test_name,
                ab_test_variant=ab_test_variant
            )
        
        # Calculate initial lead score
        lead_score = calculate_lead_score(lead)
        lead.lead_score = lead_score
        lead.save()
        
        # Record conversion event
        record_lead_capture_conversion(lead, request)
        
        # Sync to CRM
        try:
            crm_service.sync_lead(lead)
        except Exception as e:
            logger.error(f"Failed to sync lead to CRM: {e}")
        
        # Track A/B test conversion
        if ab_test_name and ab_test_variant:
            try:
                from apps.ab_testing.services import ab_testing_service
                user_identifier = lead.email or request.session.session_key or 'anonymous'
                ab_testing_service.track_conversion(
                    ab_test_name,
                    user_identifier,
                    lead,
                    conversion_type='lead_created'
                )
            except Exception as e:
                logger.error(f"Failed to track A/B test conversion: {e}")
        
        # Send webhook
        try:
            from apps.webhooks.services import webhook_service
            webhook_service.send_webhook(
                'lead_created',
                {
                    'id': str(lead.id),
                    'email': lead.email,
                    'first_name': lead.first_name,
                    'last_name': lead.last_name,
                    'company': lead.company,
                    'lead_score': lead.lead_score,
                    'status': lead.status,
                    'ab_test_variant': ab_test_variant,
                    'created_at': lead.created_at.isoformat(),
                },
                entity_id=str(lead.id)
            )
        except Exception as e:
            logger.error(f"Failed to send webhook: {e}")
        
        return Response({
            'success': True,
            'lead_id': str(lead.id),
            'lead_score': lead_score,
            'message': 'Lead captured successfully'
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def track_lead_event(request, pk):
    """
    Public endpoint to track engagement events for a lead
    Updates lead score dynamically based on engagement
    """
    try:
        lead = Lead.objects.get(pk=pk)
    except Lead.DoesNotExist:
        return Response({
            'error': 'Lead not found.'
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = LeadTrackEventSerializer(data=request.data)
    
    if serializer.is_valid():
        # Extract metadata
        session_id = serializer.validated_data.get('session_id') or request.session.session_key
        page_url = serializer.validated_data.get('page_url') or request.META.get('HTTP_REFERER', '')
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Create event
        event = Event.objects.create(
            event_name=serializer.validated_data['event_name'],
            event_category='user_interaction',
            event_properties=serializer.validated_data.get('event_properties', {}),
            session_id=session_id or 'unknown',
            page_url=page_url,
            user_identifier=lead.email,
            metadata={
                'ip_address': ip_address,
                'user_agent': user_agent
            }
        )
        
        # Update lead score based on engagement
        engagement_score = calculate_engagement_score(lead)
        lead.lead_score = min(100, lead.lead_score + engagement_score)
        lead.save()
        
        return Response({
            'success': True,
            'event_id': str(event.id),
            'updated_lead_score': lead.lead_score,
            'message': 'Event tracked successfully'
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LeadViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing leads.
    
    **Authentication:** Required (Admin only)
    
    **Permissions:** IsAuthenticated, IsAdminUser
    
    **Actions:**
    - GET /api/leads/: List all leads (paginated)
    - GET /api/leads/{id}/: Retrieve a specific lead
    - PATCH /api/leads/{id}/: Update a lead
    - DELETE /api/leads/{id}/: Delete a lead
    - POST /api/leads/{id}/qualify/: Qualify a lead
    - POST /api/leads/{id}/convert/: Convert a lead to customer
    
    **Query Parameters:**
    - status: Filter by status (new, contacted, qualified, converted, lost)
    - lifecycle_stage: Filter by lifecycle stage
    - score_min: Minimum lead score
    - score_max: Maximum lead score
    - source: Filter by lead source
    - assigned_to: Filter by assigned user ID
    - search: Search in name, email, company
    - ordering: Order by field (created_at, lead_score, status)
    
    **Example Response:**
    ```json
    {
        "count": 50,
        "next": null,
        "previous": null,
        "results": [
            {
                "id": "uuid",
                "first_name": "Jane",
                "last_name": "Smith",
                "email": "jane@example.com",
                "lead_score": 75,
                "status": "qualified",
                "lifecycle_stage": "sales_qualified"
            }
        ]
    }
    ```
    """
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['first_name', 'last_name', 'email', 'company', 'job_title']
    ordering_fields = ['created_at', 'lead_score', 'status', 'lifecycle_stage']
    ordering = ['-lead_score', '-created_at']
    
    def get_queryset(self):
        """Filter queryset based on query parameters"""
        queryset = Lead.objects.all()
        
        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by lifecycle stage
        stage_filter = self.request.query_params.get('lifecycle_stage', None)
        if stage_filter:
            queryset = queryset.filter(lifecycle_stage=stage_filter)
        
        # Filter by score range
        score_min = self.request.query_params.get('score_min', None)
        score_max = self.request.query_params.get('score_max', None)
        if score_min:
            queryset = queryset.filter(lead_score__gte=score_min)
        if score_max:
            queryset = queryset.filter(lead_score__lte=score_max)
        
        # Filter by source
        source_filter = self.request.query_params.get('source', None)
        if source_filter:
            queryset = queryset.filter(lead_source=source_filter)
        
        # Filter by assigned_to
        assigned_to = self.request.query_params.get('assigned_to', None)
        if assigned_to:
            queryset = queryset.filter(assigned_to_id=assigned_to)
        
        return queryset
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve single lead with engagement history"""
        instance = self.get_object()
        serializer = LeadDetailSerializer(instance)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        """Update lead information"""
        instance = self.get_object()
        serializer = LeadUpdateSerializer(instance, data=request.data, partial=True)
        
        if serializer.is_valid():
            # Recalculate score if relevant fields changed
            if any(field in serializer.validated_data for field in 
                   ['company', 'job_title', 'industry', 'company_size']):
                instance.lead_score = calculate_lead_score(instance)
            
            serializer.save()
            return Response(LeadSerializer(instance).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def qualify(self, request, pk=None):
        """Mark lead as qualified"""
        lead = self.get_object()
        lead.qualify()
        
        # Sync status change to CRM (creates deal for qualified leads)
        try:
            from apps.integrations.crm_service import crm_service
            # Get contact ID from CRM if exists
            if crm_service.provider and crm_service.provider_name == 'hubspot':
                from apps.integrations.hubspot_service import hubspot_service
                contact_result = hubspot_service.search_contact_by_email(lead.email)
                if contact_result:
                    contact_id = contact_result.get('id')
                    # Create deal for qualified lead
                    deal_data = {
                        'name': f"Deal for {lead.first_name} {lead.last_name}",
                        'value': None,
                        'stage': 'qualifiedtobuy',
                    }
                    hubspot_service.create_deal(deal_data, associated_contact_id=contact_id)
        except Exception as e:
            logger.error(f"Failed to sync qualification to CRM: {e}")
        
        # Send webhook
        try:
            from apps.webhooks.services import webhook_service
            webhook_service.send_webhook(
                'lead_qualified',
                {
                    'id': str(lead.id),
                    'email': lead.email,
                    'first_name': lead.first_name,
                    'last_name': lead.last_name,
                    'lead_score': lead.lead_score,
                    'status': lead.status,
                    'lifecycle_stage': lead.lifecycle_stage,
                },
                entity_id=str(lead.id)
            )
        except Exception as e:
            logger.error(f"Failed to send webhook: {e}")
        
        return Response({
            'success': True,
            'message': f'Lead {lead.email} has been qualified',
            'lead': LeadSerializer(lead).data
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def convert(self, request, pk=None):
        """Convert lead to customer"""
        lead = self.get_object()
        lead.convert()
        
        # Record conversion event
        record_lead_conversion(lead, request)
        
        # Send webhook
        try:
            from apps.webhooks.services import webhook_service
            webhook_service.send_webhook(
                'lead_converted',
                {
                    'id': str(lead.id),
                    'email': lead.email,
                    'first_name': lead.first_name,
                    'last_name': lead.last_name,
                    'lead_score': lead.lead_score,
                    'status': lead.status,
                    'lifecycle_stage': lead.lifecycle_stage,
                    'converted_at': lead.converted_at.isoformat() if lead.converted_at else None,
                },
                entity_id=str(lead.id)
            )
        except Exception as e:
            logger.error(f"Failed to send webhook: {e}")
        
        return Response({
            'success': True,
            'message': f'Lead {lead.email} has been converted to customer',
            'lead': LeadSerializer(lead).data
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get lead pipeline statistics"""
        queryset = self.get_queryset()
        
        # Total leads
        total_leads = queryset.count()
        
        # By status
        by_status = queryset.values('status').annotate(count=Count('id')).order_by('status')
        status_dict = {item['status']: item['count'] for item in by_status}
        
        # By lifecycle stage
        by_stage = queryset.values('lifecycle_stage').annotate(count=Count('id')).order_by('lifecycle_stage')
        stage_dict = {item['lifecycle_stage']: item['count'] for item in by_stage}
        
        # By source
        by_source = queryset.values('lead_source').annotate(count=Count('id')).order_by('-count')
        source_dict = {item['lead_source']: item['count'] for item in by_source}
        
        # Score distribution
        score_stats = queryset.aggregate(
            avg_score=Avg('lead_score'),
            max_score=Max('lead_score'),
            min_score=Min('lead_score')
        )
        
        # Score ranges
        score_ranges = {
            'high': queryset.filter(lead_score__gte=70).count(),
            'medium': queryset.filter(lead_score__gte=40, lead_score__lt=70).count(),
            'low': queryset.filter(lead_score__lt=40).count()
        }
        
        # Conversion rates
        converted = queryset.filter(status='converted').count()
        conversion_rate = (converted / total_leads * 100) if total_leads > 0 else 0
        
        qualified = queryset.filter(status='qualified').count()
        qualification_rate = (qualified / total_leads * 100) if total_leads > 0 else 0
        
        return Response({
            'total_leads': total_leads,
            'by_status': status_dict,
            'by_lifecycle_stage': stage_dict,
            'by_source': source_dict,
            'score_statistics': score_stats,
            'score_distribution': score_ranges,
            'conversion_rate': round(conversion_rate, 2),
            'qualification_rate': round(qualification_rate, 2),
            'converted_count': converted,
            'qualified_count': qualified
        }, status=status.HTTP_200_OK)


def calculate_lead_score(lead):
    """
    Calculate lead score based on:
    - Company size
    - Job title/role
    - Engagement level
    - Form completeness
    - Website activity
    """
    score = 0
    
    # Company size scoring
    if lead.company_size:
        size_scores = {
            '1000+': 30,
            '201-1000': 25,
            '51-200': 20,
            '11-50': 15,
            '1-10': 10
        }
        score += size_scores.get(lead.company_size, 5)
    
    # Job title/role scoring
    if lead.job_title:
        role_lower = lead.job_title.lower()
        if any(title in role_lower for title in ['ceo', 'founder', 'president', 'owner', 'director', 'vp', 'vice president']):
            score += 25
        elif any(title in role_lower for title in ['manager', 'head', 'lead', 'senior']):
            score += 15
        elif any(title in role_lower for title in ['engineer', 'developer', 'analyst', 'specialist']):
            score += 10
        else:
            score += 5
    
    # Form completeness scoring
    fields_completed = sum([
        1 if lead.first_name else 0,
        1 if lead.last_name else 0,
        1 if lead.email else 0,
        1 if lead.phone else 0,
        1 if lead.company else 0,
        1 if lead.job_title else 0,
        1 if lead.industry else 0,
        1 if lead.company_size else 0,
    ])
    completeness_score = (fields_completed / 8) * 20  # Max 20 points
    score += completeness_score
    
    # Engagement level scoring
    engagement_score = calculate_engagement_score(lead)
    score += engagement_score
    
    # Industry scoring
    if lead.industry:
        high_value_industries = ['technology', 'finance', 'healthcare']
        if lead.industry.lower() in high_value_industries:
            score += 10
        else:
            score += 5
    
    return min(100, int(score))


def calculate_engagement_score(lead):
    """Calculate engagement score based on website activity"""
    score = 0
    
    # Count events
    event_count = Event.objects.filter(user_identifier=lead.email).count()
    score += min(20, event_count * 2)  # Max 20 points for events
    
    # Check for specific engagement events
    engagement_events = Event.objects.filter(
        user_identifier=lead.email,
        event_name__in=['form_submit', 'download', 'video_play', 'demo_request']
    ).count()
    score += engagement_events * 5  # 5 points per engagement event
    
    # Check for conversions
    ct = ContentType.objects.get_for_model(Lead)
    conversion_count = Conversion.objects.filter(
        content_type=ct,
        object_id=lead.id
    ).count()
    score += conversion_count * 10  # 10 points per conversion
    
    return min(30, score)  # Max 30 points for engagement


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def record_lead_capture_conversion(lead, request):
    """Record lead capture as a conversion event"""
    ct = ContentType.objects.get_for_model(Lead)
    
    # Extract attribution data
    attribution_data = {
        'referrer': request.META.get('HTTP_REFERER', ''),
        'user_agent': request.META.get('HTTP_USER_AGENT', ''),
        'ip_address': get_client_ip(request)
    }
    
    # Extract UTM parameters if present
    utm_params = {}
    for param in ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content']:
        if param in request.GET:
            utm_params[param] = request.GET[param]
    
    campaign_info = {
        'source': lead.lead_source,
        **utm_params
    }
    
    Conversion.objects.create(
        conversion_type='lead_capture',
        content_type=ct,
        object_id=lead.id,
        attribution_data=attribution_data,
        campaign_info=campaign_info
    )


def record_lead_conversion(lead, request):
    """Record lead to customer conversion"""
    ct = ContentType.objects.get_for_model(Lead)
    
    Conversion.objects.create(
        conversion_type='purchase',  # or 'signup' depending on your business
        content_type=ct,
        object_id=lead.id,
        value=None,  # Can be set if there's a monetary value
        attribution_data={},
        campaign_info={'source': lead.lead_source}
    )

