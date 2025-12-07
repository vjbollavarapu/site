"""
A/B Testing API views
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from .services import ab_testing_service
from .models import ABTest


@api_view(['GET'])
@permission_classes([AllowAny])
def get_variant(request, test_name):
    """
    Get variant assignment for a user in an A/B test
    
    GET /api/ab-testing/variant/{test_name}/
    Query params:
    - user_identifier: Email, session_id, or other unique identifier
    
    Returns:
    {
        "variant": "A" or "B",
        "test_name": "...",
        "variant_name": "..."
    }
    """
    user_identifier = request.query_params.get('user_identifier')
    
    if not user_identifier:
        return Response({
            'error': 'user_identifier parameter is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    variant = ab_testing_service.get_variant(test_name, user_identifier)
    
    if variant is None:
        return Response({
            'error': f'A/B test "{test_name}" not found or not active'
        }, status=status.HTTP_404_NOT_FOUND)
    
    try:
        test = ABTest.objects.get(name=test_name)
        variant_name = test.variant_a_name if variant == 'A' else test.variant_b_name
        
        return Response({
            'variant': variant,
            'test_name': test_name,
            'variant_name': variant_name
        }, status=status.HTTP_200_OK)
    except ABTest.DoesNotExist:
        return Response({
            'error': f'A/B test "{test_name}" not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_test_results(request, test_name):
    """
    Get A/B test results (admin only)
    
    GET /api/ab-testing/results/{test_name}/
    """
    results = ab_testing_service.get_test_results(test_name)
    
    if results is None:
        return Response({
            'error': f'A/B test "{test_name}" not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    return Response(results, status=status.HTTP_200_OK)

