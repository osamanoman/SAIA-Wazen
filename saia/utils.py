"""
SAIA Utility Functions

This module provides common utility functions used across the SAIA system,
reducing code duplication and improving maintainability.
"""

import re
import logging
from typing import Optional, Dict, Any
from django.conf import settings

logger = logging.getLogger(__name__)


def detect_arabic_text(text: str) -> bool:
    """
    Efficiently detect Arabic text in user input.
    
    Args:
        text: Input text to analyze
        
    Returns:
        bool: True if text appears to be primarily Arabic
    """
    if not text or len(text) == 0:
        return False
    
    # Check first 100 characters for efficiency
    sample = text[:100]
    
    # Count Arabic Unicode characters (Arabic block: U+0600 to U+06FF)
    arabic_chars = sum(1 for char in sample if 0x0600 <= ord(char) <= 0x06FF)
    
    # Also count other non-ASCII characters that might be Arabic
    non_ascii_chars = sum(1 for char in sample if ord(char) > 127)
    
    # Consider it Arabic if:
    # 1. Has Arabic Unicode characters, OR
    # 2. More than 30% of characters are non-ASCII (fallback for mixed content)
    return arabic_chars > 0 or non_ascii_chars > len(sample) * 0.3


def sanitize_search_query(query: str, max_length: int = 500) -> Optional[str]:
    """
    Sanitize and validate search query input.
    
    Args:
        query: Raw search query
        max_length: Maximum allowed query length
        
    Returns:
        str: Sanitized query or None if invalid
    """
    if not query or not isinstance(query, str):
        return None
    
    # Remove potentially harmful characters and normalize whitespace
    query = re.sub(r'[<>"\';\\]', '', query)  # Remove potentially harmful chars
    query = re.sub(r'\s+', ' ', query.strip())  # Normalize whitespace
    
    # Limit length
    query = query[:max_length]
    
    # Ensure minimum length
    if len(query) < 2:
        return None
    
    return query


def get_company_config(company_name: str, config_key: str, default: Any = None) -> Any:
    """
    Get company-specific configuration value.
    
    Args:
        company_name: Name of the company
        config_key: Configuration key to retrieve
        default: Default value if not found
        
    Returns:
        Configuration value or default
    """
    company_configs = getattr(settings, 'COMPANY_CONFIGS', {})
    company_config = company_configs.get(company_name.lower(), {})
    return company_config.get(config_key, default)


def should_use_hybrid_assistant(company_name: str) -> bool:
    """
    Determine if a company should use the hybrid assistant.
    
    Args:
        company_name: Name of the company
        
    Returns:
        bool: True if company should use hybrid assistant
    """
    hybrid_companies = getattr(settings, 'HYBRID_ASSISTANT_COMPANIES', ['wazen'])
    return company_name.lower() in [name.lower() for name in hybrid_companies]


def format_knowledge_response(content: str, is_arabic: bool, source: str = "knowledge base") -> str:
    """
    Format knowledge base response with appropriate language prefix.
    
    Args:
        content: Knowledge base content
        is_arabic: Whether to use Arabic formatting
        source: Source description for the content
        
    Returns:
        str: Formatted response
    """
    if is_arabic:
        return f"بناءً على {source}:\n\n{content}"
    else:
        return f"Based on our {source}:\n\n{content}"


def get_error_message(error_type: str, is_arabic: bool) -> str:
    """
    Get localized error message.
    
    Args:
        error_type: Type of error (search_error, general_error, etc.)
        is_arabic: Whether to return Arabic message
        
    Returns:
        str: Localized error message
    """
    error_messages = {
        'search_error': {
            'ar': "عذراً، حدث خطأ أثناء البحث في قاعدة المعرفة. يرجى المحاولة مرة أخرى أو التواصل مع فريق الدعم.",
            'en': "Sorry, there was an error searching our knowledge base. Please try again or contact our support team."
        },
        'no_results': {
            'ar': "عذراً، لم أجد معلومات محددة حول استفسارك في قاعدة المعرفة. يرجى المحاولة بكلمات مختلفة أو التواصل مع فريق الدعم.",
            'en': "I'm sorry, I couldn't find specific information about your query in our knowledge base. Please try different keywords or contact our support team."
        },
        'general_error': {
            'ar': "أعتذر، أواجه صعوبات تقنية. يرجى المحاولة مرة أخرى لاحقاً.",
            'en': "I apologize, but I'm experiencing technical difficulties. Please try again later."
        },
        'welcome': {
            'ar': "مرحباً بك في وازن للتأمين. يمكنني مساعدتك في الاستفسارات العامة حول خدماتنا وسياساتنا ودعمنا. هل هناك شيء محدد تود معرفته؟",
            'en': "Welcome to Wazen Insurance. I can help you with general inquiries about our services, policies, and support. Is there something specific you'd like to know?"
        }
    }
    
    lang = 'ar' if is_arabic else 'en'
    return error_messages.get(error_type, {}).get(lang, "I'm here to help you. / أنا هنا لمساعدتك.")


def log_security_event(event_type: str, user, details: Dict[str, Any] = None):
    """
    Log security-related events for monitoring.
    
    Args:
        event_type: Type of security event
        user: User object or username
        details: Additional event details
    """
    username = getattr(user, 'username', str(user)) if user else 'anonymous'
    company = getattr(user, 'company', None) if user else None
    company_name = company.name if company else 'unknown'
    
    logger.warning(
        f"SECURITY_EVENT: {event_type} | User: {username} | Company: {company_name} | Details: {details or {}}"
    )


def validate_model_constraints(model_instance, field_constraints: Dict[str, Any]) -> Dict[str, str]:
    """
    Validate model instance against custom constraints.
    
    Args:
        model_instance: Django model instance
        field_constraints: Dictionary of field constraints
        
    Returns:
        Dict of field errors
    """
    errors = {}
    
    for field_name, constraints in field_constraints.items():
        value = getattr(model_instance, field_name, None)
        
        if 'required' in constraints and constraints['required'] and not value:
            errors[field_name] = f"{field_name} is required"
        
        if 'max_length' in constraints and value and len(str(value)) > constraints['max_length']:
            errors[field_name] = f"{field_name} exceeds maximum length of {constraints['max_length']}"
        
        if 'min_length' in constraints and value and len(str(value)) < constraints['min_length']:
            errors[field_name] = f"{field_name} must be at least {constraints['min_length']} characters"
    
    return errors
