"""
Spam detection service for contact submissions
"""
import re
from django.conf import settings
from django.utils import timezone
from django_ratelimit.core import is_ratelimited
from .security import verify_recaptcha


class CheckSubmissionSpam:
    """
    Service class for comprehensive spam detection
    """
    
    # Suspicious keywords
    SPAM_KEYWORDS = [
        'viagra', 'casino', 'lottery', 'winner', 'click here', 'limited time',
        'act now', 'urgent', 'free money', 'guaranteed', 'no risk',
        'work from home', 'make money fast', 'get rich', 'debt consolidation',
        'weight loss', 'miracle cure', 'one weird trick', 'you won',
        'congratulations', 'claim now', 'exclusive offer', 'limited offer'
    ]
    
    # Blacklisted email domains
    BLACKLISTED_DOMAINS = [
        'tempmail', '10minutemail', 'guerrillamail', 'mailinator',
        'throwaway', 'trashmail', 'getnada', 'mohmal', 'yopmail',
        'fakeinbox', 'dispostable', 'maildrop'
    ]
    
    # Blacklisted email addresses (can be loaded from database or file)
    BLACKLISTED_EMAILS = []
    
    # Link count threshold
    MAX_LINKS = 3
    
    # Caps ratio threshold
    CAPS_RATIO_THRESHOLD = 0.7
    
    def __init__(self, submission_data, request=None):
        """
        Initialize spam checker with submission data and optional request
        """
        self.data = submission_data
        self.request = request
        self.spam_score = 0.0
        self.reasons = []
        self.logs = []
    
    def check_honeypot(self, honeypot_value):
        """
        Verify honeypot field - should be empty
        Returns: (is_spam: bool, score: float)
        """
        if honeypot_value and honeypot_value.strip():
            self.spam_score += 1.0  # Immediate spam if honeypot filled
            self.reasons.append("Honeypot field filled")
            self.logs.append(f"Honeypot check failed: field contains '{honeypot_value[:20]}'")
            return True, 1.0
        return False, 0.0
    
    def check_recaptcha(self, token):
        """
        Verify reCAPTCHA score
        Returns: (is_spam: bool, score: float)
        """
        recaptcha_secret = getattr(settings, 'RECAPTCHA_SECRET_KEY', None)
        if not recaptcha_secret:
            # reCAPTCHA not configured, skip check
            return False, 0.0
        
        if not token:
            self.spam_score += 0.3
            self.reasons.append("Missing reCAPTCHA token")
            self.logs.append("reCAPTCHA token missing")
            return False, 0.3
        
        success, score, error = verify_recaptcha(token, recaptcha_secret)
        
        if not success:
            self.spam_score += 0.5
            self.reasons.append(f"reCAPTCHA verification failed: {error}")
            self.logs.append(f"reCAPTCHA verification failed: {error}")
            return True, 0.5
        
        required_score = getattr(settings, 'RECAPTCHA_REQUIRED_SCORE', 0.5)
        if score < required_score:
            self.spam_score += (required_score - score) * 0.5
            self.reasons.append(f"Low reCAPTCHA score: {score}")
            self.logs.append(f"Low reCAPTCHA score: {score} (required: {required_score})")
            return score < 0.3, (required_score - score) * 0.5
        
        return False, 0.0
    
    def check_content(self):
        """
        Analyze message content for spam indicators
        Returns: (is_spam: bool, score: float)
        """
        message = self.data.get('message', '').lower()
        email = self.data.get('email', '').lower()
        name = self.data.get('name', '').lower()
        subject = self.data.get('subject', '').lower()
        
        content_score = 0.0
        
        # Check for suspicious keywords
        for keyword in self.SPAM_KEYWORDS:
            if keyword in message or keyword in name or keyword in subject:
                content_score += 0.15
                self.reasons.append(f"Suspicious keyword: {keyword}")
                self.logs.append(f"Found spam keyword: {keyword}")
        
        # Check link count
        link_pattern = r'https?://[^\s]+'
        links = re.findall(link_pattern, message)
        if len(links) > self.MAX_LINKS:
            content_score += 0.2
            self.reasons.append(f"Too many links: {len(links)}")
            self.logs.append(f"Excessive links detected: {len(links)}")
        
        # Check for ALL CAPS
        if message and len(message) > 20:
            caps_ratio = sum(1 for c in message if c.isupper()) / len(message)
            if caps_ratio > self.CAPS_RATIO_THRESHOLD:
                content_score += 0.1
                self.reasons.append("Excessive capitalization")
                self.logs.append(f"High caps ratio: {caps_ratio:.2f}")
        
        # Check for repetitive patterns
        if message:
            repeated_pattern = r'(.)\1{4,}'
            if re.search(repeated_pattern, message):
                content_score += 0.1
                self.reasons.append("Repeated characters detected")
                self.logs.append("Repetitive pattern found")
        
        # Check for suspicious patterns
        spam_patterns = [
            r'\d{4,}',  # Long number sequences
            r'[!@#$%^&*()]{3,}',  # Multiple special characters
            r'(.)\1{10,}',  # Very long repeated characters
        ]
        
        for pattern in spam_patterns:
            if re.search(pattern, message):
                content_score += 0.1
                self.reasons.append("Suspicious pattern detected")
                self.logs.append(f"Suspicious pattern: {pattern}")
                break
        
        # Check email domain
        for domain in self.BLACKLISTED_DOMAINS:
            if domain in email:
                content_score += 0.3
                self.reasons.append(f"Blacklisted email domain: {domain}")
                self.logs.append(f"Blacklisted domain: {domain}")
                break
        
        # Check blacklisted emails
        if email in self.BLACKLISTED_EMAILS:
            content_score += 1.0
            self.reasons.append("Blacklisted email address")
            self.logs.append(f"Blacklisted email: {email}")
        
        # Email format validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            content_score += 0.2
            self.reasons.append("Invalid email format")
            self.logs.append("Invalid email format")
        
        # Very short messages
        if len(message) < 15:
            content_score += 0.1
            self.reasons.append("Message too short")
            self.logs.append(f"Message too short: {len(message)} chars")
        
        self.spam_score += content_score
        return content_score > 0.5, content_score
    
    def check_rate_limit(self):
        """
        Verify IP rate limit
        Returns: (is_rate_limited: bool)
        """
        if not self.request:
            return False
        
        # Check if rate limited (5 per hour for forms)
        if is_ratelimited(self.request, group='contact-spam-check', key='ip', rate='5/h', method='POST', increment=False):
            self.reasons.append("Rate limit exceeded")
            self.logs.append("IP rate limit exceeded")
            return True
        return False
    
    def calculate_spam_score(self, honeypot_value=None, recaptcha_token=None):
        """
        Calculate comprehensive spam score
        Returns: (is_spam: bool, spam_score: float, reasons: list, logs: list)
        """
        self.spam_score = 0.0
        self.reasons = []
        self.logs = []
        
        # Check honeypot
        if honeypot_value is not None:
            is_honeypot_spam, score = self.check_honeypot(honeypot_value)
            if is_honeypot_spam:
                # Honeypot filled = immediate spam
                return True, 1.0, self.reasons, self.logs
        
        # Check reCAPTCHA
        if recaptcha_token is not None:
            is_recaptcha_spam, score = self.check_recaptcha(recaptcha_token)
            if is_recaptcha_spam and score >= 0.5:
                # High reCAPTCHA failure = likely spam
                return True, min(1.0, self.spam_score), self.reasons, self.logs
        
        # Check rate limit
        if self.check_rate_limit():
            # Rate limited = likely spam
            return True, 1.0, self.reasons, self.logs
        
        # Check content
        is_content_spam, content_score = self.check_content()
        
        # Final score calculation
        final_score = min(1.0, self.spam_score)
        is_spam = final_score > 0.7
        
        # Log spam attempt if detected
        if is_spam:
            self._log_spam_attempt()
        
        return is_spam, final_score, self.reasons, self.logs
    
    def _log_spam_attempt(self):
        """
        Log spam attempt for analysis
        In production, this could write to a database or logging service
        """
        import logging
        logger = logging.getLogger('spam_detection')
        
        log_data = {
            'email': self.data.get('email', ''),
            'ip_address': get_client_ip(self.request) if self.request else 'unknown',
            'spam_score': self.spam_score,
            'reasons': self.reasons,
            'timestamp': str(timezone.now())
        }
        
        logger.warning(f"Spam attempt detected: {log_data}")


def get_client_ip(request):
    """Get client IP address from request"""
    if not request:
        return None
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip



