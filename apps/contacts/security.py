"""
Security utilities for contact submissions and other forms
"""
import re
from django.utils.html import strip_tags, escape
from django.core.exceptions import ValidationError


def sanitize_input(text):
    """
    Sanitize user input to prevent XSS attacks
    """
    if not text:
        return text
    
    # Remove HTML tags
    text = strip_tags(str(text))
    
    # Escape special characters
    text = escape(text)
    
    return text.strip()


def detect_spam(data):
    """
    Enhanced spam detection with multiple heuristics
    Returns: (is_spam: bool, spam_score: float, reasons: list)
    """
    spam_score = 0.0
    reasons = []
    
    message = data.get('message', '').lower()
    email = data.get('email', '').lower()
    name = data.get('name', '').lower()
    subject = data.get('subject', '').lower()
    
    # Suspicious keywords
    spam_keywords = [
        'viagra', 'casino', 'lottery', 'winner', 'click here', 'limited time',
        'act now', 'urgent', 'free money', 'guaranteed', 'no risk',
        'work from home', 'make money fast', 'get rich', 'debt consolidation'
    ]
    
    for keyword in spam_keywords:
        if keyword in message or keyword in name or keyword in subject:
            spam_score += 0.15
            reasons.append(f"Suspicious keyword: {keyword}")
    
    # Excessive links
    link_pattern = r'https?://[^\s]+'
    links = re.findall(link_pattern, message)
    if len(links) > 3:
        spam_score += 0.2
        reasons.append(f"Too many links: {len(links)}")
    
    # ALL CAPS detection
    if message and len(message) > 20:
        caps_ratio = sum(1 for c in message if c.isupper()) / len(message)
        if caps_ratio > 0.7:
            spam_score += 0.1
            reasons.append("Excessive capitalization")
    
    # Repeated characters
    if message:
        repeated_pattern = r'(.)\1{4,}'
        if re.search(repeated_pattern, message):
            spam_score += 0.1
            reasons.append("Repeated characters detected")
    
    # Suspicious email domains
    suspicious_domains = [
        'tempmail', '10minutemail', 'guerrillamail', 'mailinator',
        'throwaway', 'trashmail', 'getnada', 'mohmal'
    ]
    
    for domain in suspicious_domains:
        if domain in email:
            spam_score += 0.3
            reasons.append(f"Suspicious email domain: {domain}")
            break
    
    # Very short messages
    if len(message) < 15:
        spam_score += 0.1
        reasons.append("Message too short")
    
    # Email format validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        spam_score += 0.2
        reasons.append("Invalid email format")
    
    # Check for common spam patterns
    spam_patterns = [
        r'\d{4,}',  # Long number sequences
        r'[!@#$%^&*()]{3,}',  # Multiple special characters
    ]
    
    for pattern in spam_patterns:
        if re.search(pattern, message):
            spam_score += 0.1
            reasons.append("Suspicious pattern detected")
    
    is_spam = spam_score >= 0.7
    
    return is_spam, min(1.0, spam_score), reasons


def validate_honeypot(honeypot_value):
    """
    Validate honeypot field - should be empty
    """
    if honeypot_value and honeypot_value.strip():
        raise ValidationError("Spam detected: honeypot field filled")


def verify_recaptcha(token, secret_key):
    """
    Verify reCAPTCHA token server-side
    Returns: (success: bool, score: float, error: str)
    """
    import requests
    
    if not token:
        return False, 0.0, "No reCAPTCHA token provided"
    
    if not secret_key:
        return False, 0.0, "reCAPTCHA secret key not configured"
    
    try:
        response = requests.post(
            'https://www.google.com/recaptcha/api/siteverify',
            data={
                'secret': secret_key,
                'response': token
            },
            timeout=5
        )
        
        data = response.json()
        
        if data.get('success'):
            score = data.get('score', 0.0)
            return True, score, None
        else:
            error_codes = data.get('error-codes', [])
            return False, 0.0, f"reCAPTCHA verification failed: {', '.join(error_codes)}"
    
    except requests.RequestException as e:
        return False, 0.0, f"reCAPTCHA verification error: {str(e)}"

