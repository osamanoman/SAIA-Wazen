"""
Security utilities for the widget API.

This module provides rate limiting, input validation, CORS handling,
and other security features for the chatbot widget API endpoints.
"""

import re
import json
import hashlib
from functools import wraps
from django.http import JsonResponse
from django.core.cache import cache
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# Rate limiting configuration
RATE_LIMITS = {
    'widget_config': {'requests': 10000, 'window': 3600},  # 10000 requests per hour (increased for development)
    'session_create': {'requests': 100, 'window': 3600},   # 100 sessions per hour per IP (increased for testing)
    'message_send': {'requests': 600, 'window': 3600},     # 600 messages per hour per session (increased for testing)
    'handover_request': {'requests': 50, 'window': 3600},  # 50 handover requests per hour (increased for testing)
}

# Input validation patterns
COMPANY_SLUG_PATTERN = re.compile(r'^[a-zA-Z0-9_-]+$')
SESSION_ID_PATTERN = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
CONTENT_MAX_LENGTH = 2000

# Allowed origins for CORS (can be configured via settings)
ALLOWED_ORIGINS = getattr(settings, 'WIDGET_ALLOWED_ORIGINS', ['*'])


def get_client_ip(request):
    """Get the real client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_rate_limit_key(request, endpoint, identifier=None):
    """Generate a unique key for rate limiting."""
    client_ip = get_client_ip(request)
    base_key = f"rate_limit:{endpoint}:{client_ip}"
    
    if identifier:
        # Hash the identifier to keep keys short
        identifier_hash = hashlib.md5(str(identifier).encode()).hexdigest()[:8]
        base_key += f":{identifier_hash}"
    
    return base_key


def is_rate_limited(request, endpoint, identifier=None):
    """Check if request should be rate limited."""
    if endpoint not in RATE_LIMITS:
        return False
    
    config = RATE_LIMITS[endpoint]
    key = get_rate_limit_key(request, endpoint, identifier)
    
    # Get current count
    current_count = cache.get(key, 0)
    
    # Check if limit exceeded
    if current_count >= config['requests']:
        logger.warning(f"Rate limit exceeded for {key}: {current_count}/{config['requests']}")
        return True
    
    # Increment counter
    cache.set(key, current_count + 1, config['window'])
    return False


def rate_limit(endpoint):
    """Decorator to apply rate limiting to views."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Extract identifier from URL parameters if available
            identifier = None
            if 'session_id' in kwargs:
                identifier = kwargs['session_id']
            elif 'company_slug' in kwargs:
                identifier = kwargs['company_slug']
            
            if is_rate_limited(request, endpoint, identifier):
                return JsonResponse({
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Please try again later."
                }, status=429)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def validate_input(data, field, pattern=None, max_length=None, required=True):
    """Validate a single input field."""
    value = data.get(field)
    
    if required and not value:
        return f"Field '{field}' is required"
    
    if not required and not value:
        return None  # Optional field, no value provided
    
    if isinstance(value, str):
        value = value.strip()
        
        if max_length and len(value) > max_length:
            return f"Field '{field}' exceeds maximum length of {max_length}"
        
        if pattern and not pattern.match(value):
            return f"Field '{field}' contains invalid characters"
    
    return None


def sanitize_content(content):
    """Sanitize user content to prevent XSS and other attacks."""
    if not isinstance(content, str):
        return content

    # Simple but effective HTML escaping for chat messages
    import html

    # HTML escape all content - no HTML allowed in chat messages
    sanitized = html.escape(content, quote=True)

    # Additional cleanup of dangerous patterns
    dangerous_patterns = [
        r'javascript:',
        r'data:',
        r'vbscript:',
    ]

    for pattern in dangerous_patterns:
        sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)

    return sanitized.strip()


def validate_widget_request(required_fields):
    """Decorator to validate widget API requests."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            try:
                # Parse JSON data
                if request.body:
                    data = json.loads(request.body)
                else:
                    data = {}
                
                # Validate required fields
                errors = []
                for field in required_fields:
                    error = validate_input(data, field, required=True)
                    if error:
                        errors.append(error)
                
                if errors:
                    return JsonResponse({
                        "error": "Validation failed",
                        "details": errors
                    }, status=400)
                
                # Sanitize content fields
                if 'content' in data:
                    data['content'] = sanitize_content(data['content'])
                    if len(data['content']) > CONTENT_MAX_LENGTH:
                        return JsonResponse({
                            "error": "Content too long",
                            "message": f"Content must be less than {CONTENT_MAX_LENGTH} characters"
                        }, status=400)
                
                # Add sanitized data to request for use in view
                request.validated_data = data
                
            except json.JSONDecodeError:
                return JsonResponse({
                    "error": "Invalid JSON",
                    "message": "Request body must be valid JSON"
                }, status=400)
            except Exception as e:
                logger.error(f"Validation error: {e}")
                return JsonResponse({
                    "error": "Validation error",
                    "message": "Failed to validate request"
                }, status=400)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def is_origin_allowed(origin):
    """Check if the origin is allowed for CORS."""
    if not origin:
        return False
    
    if '*' in ALLOWED_ORIGINS:
        return True
    
    return origin in ALLOWED_ORIGINS


def add_cors_headers(response, origin=None):
    """Add CORS headers to response."""
    if origin and is_origin_allowed(origin):
        response['Access-Control-Allow-Origin'] = origin
    elif '*' in ALLOWED_ORIGINS:
        response['Access-Control-Allow-Origin'] = '*'
    
    response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
    response['Access-Control-Max-Age'] = '86400'  # 24 hours
    
    return response


def handle_preflight_request(request):
    """Handle CORS preflight OPTIONS requests."""
    response = JsonResponse({})
    return add_cors_headers(response, request.META.get('HTTP_ORIGIN'))
