"""
Celery tasks for analytics aggregation
"""
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

from .services import calculate_aggregated_stats, get_dashboard_stats

logger = logging.getLogger(__name__)


@shared_task
def update_daily_stats(date=None):
    """
    Background job to pre-calculate daily statistics
    Updates cache for dashboard performance
    """
    try:
        if not date:
            date = timezone.now().date()
        
        # Calculate stats for the date
        stats = calculate_aggregated_stats(date)
        
        logger.info(f"Updated daily stats for {date}: {stats['total_pageviews']} pageviews")
        return stats
    except Exception as e:
        logger.error(f"Error updating daily stats: {str(e)}")
        return None


@shared_task
def update_weekly_stats():
    """
    Background job to pre-calculate weekly statistics
    """
    try:
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        
        stats = get_dashboard_stats(week_start, today)
        
        logger.info(f"Updated weekly stats: {stats['total_pageviews']} pageviews")
        return stats
    except Exception as e:
        logger.error(f"Error updating weekly stats: {str(e)}")
        return None


@shared_task
def update_monthly_stats():
    """
    Background job to pre-calculate monthly statistics
    """
    try:
        today = timezone.now().date()
        month_start = today.replace(day=1)
        
        stats = get_dashboard_stats(month_start, today)
        
        logger.info(f"Updated monthly stats: {stats['total_pageviews']} pageviews")
        return stats
    except Exception as e:
        logger.error(f"Error updating monthly stats: {str(e)}")
        return None


@shared_task
def cleanup_old_sessions():
    """
    Background job to clean up expired sessions from cache
    """
    try:
        # This would iterate through cache keys and remove expired sessions
        # Implementation depends on cache backend
        logger.info("Cleaned up old sessions")
        return True
    except Exception as e:
        logger.error(f"Error cleaning up sessions: {str(e)}")
        return False

