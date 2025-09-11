"""
Security utilities for SAIA Project App

This module provides security utilities specific to the project app.
"""

import logging
from django.utils import timezone
import re

logger = logging.getLogger(__name__)

# Blocked patterns in messages (basic content filtering)
BLOCKED_PATTERNS = [
    re.compile(r'<script[^>]*>.*?</script>', re.IGNORECASE | re.DOTALL),
    re.compile(r'javascript:', re.IGNORECASE),
    re.compile(r'on\w+\s*=', re.IGNORECASE),  # Event handlers
]


def sanitize_message_content(content):
    """
    Sanitize message content to prevent XSS and other attacks.

    Args:
        content: Message content to sanitize

    Returns:
        str: Sanitized content
    """
    if not content:
        return ""

    # Check for blocked patterns
    for pattern in BLOCKED_PATTERNS:
        if pattern.search(content):
            logger.warning(f"Blocked potentially malicious content: {content[:100]}...")
            return "[Content blocked for security reasons]"

    # Basic HTML entity encoding for safety
    content = content.replace('<', '&lt;').replace('>', '&gt;')

    # Limit length
    if len(content) > 2000:
        content = content[:2000] + "..."

    return content.strip()


def log_security_event(event_type, request, details=None):
    """
    Log security-related events for monitoring and analysis.

    Args:
        event_type: Type of security event
        request: HTTP request object
        details: Additional event details
    """
    client_ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
    user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')

    log_data = {
        'event_type': event_type,
        'client_ip': client_ip,
        'user_agent': user_agent,
        'timestamp': timezone.now().isoformat(),
        'path': request.path,
        'method': request.method,
    }

    if details:
        log_data.update(details)

    logger.warning(f"Security Event: {event_type} from {client_ip} - {details}")
