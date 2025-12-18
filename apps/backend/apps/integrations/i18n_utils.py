"""
Internationalization utilities
"""
from django.utils import translation
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def get_user_language(request):
    """
    Get user's preferred language from request
    
    Checks:
    1. Explicit language parameter
    2. Accept-Language header
    3. Session language
    4. Default language
    
    Returns:
        str: Language code (e.g., 'en', 'es', 'fr')
    """
    # Check explicit language parameter
    lang = request.GET.get('lang') or request.POST.get('lang')
    if lang and lang in dict(settings.LANGUAGES):
        return lang
    
    # Check Accept-Language header
    accept_language = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
    if accept_language:
        # Parse Accept-Language header
        # Format: "en-US,en;q=0.9,es;q=0.8"
        languages = []
        for lang_part in accept_language.split(','):
            lang_code = lang_part.split(';')[0].strip().lower()
            # Extract base language (e.g., 'en' from 'en-US')
            base_lang = lang_code.split('-')[0]
            if base_lang in dict(settings.LANGUAGES):
                languages.append(base_lang)
        
        if languages:
            return languages[0]
    
    # Check session language
    if hasattr(request, 'session'):
        session_lang = request.session.get('django_language')
        if session_lang and session_lang in dict(settings.LANGUAGES):
            return session_lang
    
    # Return default language
    return settings.LANGUAGE_CODE.split('-')[0]


def activate_language(language_code):
    """
    Activate language for current thread
    
    Args:
        language_code: Language code to activate
    """
    try:
        translation.activate(language_code)
    except Exception as e:
        logger.warning(f"Failed to activate language {language_code}: {e}")


def get_translated_message(key, language_code=None, default=None):
    """
    Get translated message
    
    Args:
        key: Message key
        language_code: Optional language code (uses current if not provided)
        default: Default message if translation not found
    
    Returns:
        str: Translated message
    """
    if language_code:
        with translation.override(language_code):
            return translation.gettext(key) if default is None else translation.gettext(key) or default
    else:
        return translation.gettext(key) if default is None else translation.gettext(key) or default

