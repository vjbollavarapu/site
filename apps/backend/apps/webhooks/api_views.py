"""
Webhook API views
"""
import json
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .services import WebhookService
from .models import WebhookConfig


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def test_webhook(request):
    """
    Test webhook endpoint for verifying webhook configuration
    
    This endpoint can be used to test webhook delivery.
    It accepts a POST request and returns the received payload.
    """
    try:
        payload = request.data
        signature = request.headers.get('X-Webhook-Signature', '')
        event_type = request.headers.get('X-Webhook-Event', '')
        webhook_id = request.headers.get('X-Webhook-Id', '')
        
        return Response({
            'success': True,
            'message': 'Webhook received',
            'payload': payload,
            'headers': {
                'signature': signature,
                'event_type': event_type,
                'webhook_id': webhook_id,
            }
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def verify_webhook_signature(request):
    """
    Verify webhook signature
    
    POST /api/webhooks/verify/
    Body: {
        "payload": {...},
        "signature": "sha256=...",
        "secret_key": "..."
    }
    """
    try:
        payload_str = json.dumps(request.data.get('payload', {}), sort_keys=True)
        signature = request.data.get('signature', '')
        secret_key = request.data.get('secret_key', '')
        
        if not secret_key:
            return Response({
                'success': False,
                'error': 'secret_key is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        is_valid = WebhookService.verify_signature(payload_str, signature, secret_key)
        
        return Response({
            'success': True,
            'valid': is_valid
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

