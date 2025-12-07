"""
Batch processing for analytics data
"""
import logging
from collections import deque
from threading import Lock
from django.conf import settings
from django.db import transaction

logger = logging.getLogger(__name__)

BATCH_SIZE = getattr(settings, 'ANALYTICS_BATCH_SIZE', 50)
BATCH_TIMEOUT = getattr(settings, 'ANALYTICS_BATCH_TIMEOUT', 5)  # seconds


class BatchProcessor:
    """
    Batch processes analytics events for better performance
    """
    
    def __init__(self):
        self.page_views = deque()
        self.events = deque()
        self.lock = Lock()
    
    def add_page_view(self, page_view_data):
        """Add page view to batch queue"""
        with self.lock:
            self.page_views.append(page_view_data)
            if len(self.page_views) >= BATCH_SIZE:
                self._flush_page_views()
    
    def add_event(self, event_data):
        """Add event to batch queue"""
        with self.lock:
            self.events.append(event_data)
            if len(self.events) >= BATCH_SIZE:
                self._flush_events()
    
    def _flush_page_views(self):
        """Flush page views to database"""
        if not self.page_views:
            return
        
        try:
            from .models import PageView
            
            page_views_to_create = []
            page_views_data = []
            while self.page_views:
                page_view_data = self.page_views.popleft()
                page_views_data.append(page_view_data)
                page_views_to_create.append(PageView(**page_view_data))
            
            if page_views_to_create:
                with transaction.atomic():
                    PageView.objects.bulk_create(page_views_to_create, ignore_conflicts=True)
                logger.info(f"Batch created {len(page_views_to_create)} page views")
        except Exception as e:
            logger.error(f"Error flushing page views: {str(e)}")
            # Re-add to queue for retry
            for pv_data in page_views_data:
                self.page_views.append(pv_data)
    
    def _flush_events(self):
        """Flush events to database"""
        if not self.events:
            return
        
        try:
            from .models import Event
            
            events_to_create = []
            events_data = []
            while self.events:
                event_data = self.events.popleft()
                events_data.append(event_data)
                events_to_create.append(Event(**event_data))
            
            if events_to_create:
                with transaction.atomic():
                    Event.objects.bulk_create(events_to_create, ignore_conflicts=True)
                logger.info(f"Batch created {len(events_to_create)} events")
        except Exception as e:
            logger.error(f"Error flushing events: {str(e)}")
            # Re-add to queue for retry
            for ev_data in events_data:
                self.events.append(ev_data)
    
    def flush_all(self):
        """Flush all pending data"""
        with self.lock:
            self._flush_page_views()
            self._flush_events()
    
    def get_queue_sizes(self):
        """Get current queue sizes"""
        with self.lock:
            return {
                'page_views': len(self.page_views),
                'events': len(self.events),
            }


# Global batch processor instance
batch_processor = BatchProcessor()

