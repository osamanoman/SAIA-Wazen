"""
Utility functions for the widget app.

This module provides helper functions for AI assistant routing,
session management, and other widget-related operations.
"""

import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def get_company_assistant_id(company):
    """
    Get the AI assistant ID for a company.
    
    This function implements the company-specific AI routing logic.
    It tries multiple approaches to find the right assistant:
    1. Use company.get_company_assistant_id() if available
    2. Use naming convention: {company_name}_ai_assistant
    3. Fall back to default assistant if configured
    
    Args:
        company: Company model instance
        
    Returns:
        str: Assistant ID or None if no assistant found
    """
    try:
        # Method 1: Use company's built-in method if available
        if hasattr(company, 'get_company_assistant_id'):
            assistant_id = company.get_company_assistant_id()
            if assistant_id:
                # Verify the assistant exists
                try:
                    from product.assistants import COMPANY_ASSISTANTS
                    if assistant_id in COMPANY_ASSISTANTS:
                        logger.info(f"Using company assistant: {assistant_id}")
                        return assistant_id
                    else:
                        logger.warning(f"Company assistant {assistant_id} not found in registry")
                except ImportError as e:
                    logger.warning(f"Company assistants registry not available: {e}")
        
        # Method 2: Try naming convention
        company_name = company.name.lower().replace(' ', '_').replace('-', '_')
        assistant_id = f"{company_name}_ai_assistant"
        
        try:
            from product.assistants import COMPANY_ASSISTANTS
            if assistant_id in COMPANY_ASSISTANTS:
                logger.info(f"Using convention-based assistant: {assistant_id}")
                return assistant_id
            else:
                logger.warning(f"Convention-based assistant {assistant_id} not found")
        except ImportError:
            logger.warning(f"Company assistants registry not available")
        
        # Method 3: Try alternative naming patterns
        alternative_patterns = [
            f"{company_name}_assistant",
            f"{company_name}ai_assistant",
            f"{company_name}_ai",
        ]
        
        for pattern in alternative_patterns:
            try:
                from product.assistants import COMPANY_ASSISTANTS
                if pattern in COMPANY_ASSISTANTS:
                    logger.info(f"Using alternative pattern assistant: {pattern}")
                    return pattern
            except ImportError:
                continue
        
        # Method 4: Fall back to default assistant if configured
        default_assistant = getattr(settings, 'DEFAULT_WIDGET_ASSISTANT', None)
        if default_assistant:
            try:
                from product.assistants import COMPANY_ASSISTANTS
                if default_assistant in COMPANY_ASSISTANTS:
                    logger.info(f"Using default assistant: {default_assistant}")
                    return default_assistant
                else:
                    logger.warning(f"Default assistant {default_assistant} not found")
            except ImportError:
                logger.warning(f"Company assistants registry not available")
        
        logger.error(f"No AI assistant found for company: {company.name}")
        return None
        
    except Exception as e:
        logger.error(f"Error getting assistant for company {company.name}: {e}")
        return None


def format_session_duration(duration_minutes):
    """
    Format session duration in a human-readable format.
    
    Args:
        duration_minutes: Duration in minutes
        
    Returns:
        str: Formatted duration string
    """
    if duration_minutes < 1:
        return "Less than a minute"
    elif duration_minutes < 60:
        return f"{duration_minutes} minute{'s' if duration_minutes != 1 else ''}"
    else:
        hours = duration_minutes // 60
        minutes = duration_minutes % 60
        if minutes == 0:
            return f"{hours} hour{'s' if hours != 1 else ''}"
        else:
            return f"{hours} hour{'s' if hours != 1 else ''} and {minutes} minute{'s' if minutes != 1 else ''}"


def get_session_analytics(session):
    """
    Get analytics data for a session.
    
    Args:
        session: WebsiteSession instance
        
    Returns:
        dict: Analytics data
    """
    try:
        messages = session.thread.messages.all()
        
        user_messages = messages.filter(message_type='human')
        ai_messages = messages.filter(message_type='ai')
        tool_messages = messages.filter(message_type='tool')
        
        analytics = {
            'total_messages': messages.count(),
            'user_messages': user_messages.count(),
            'ai_messages': ai_messages.count(),
            'tool_calls': tool_messages.count(),
            'duration_minutes': session.duration_minutes,
            'duration_formatted': format_session_duration(session.duration_minutes),
            'messages_per_minute': round(messages.count() / max(session.duration_minutes, 1), 2),
            'visitor_info': {
                'ip': session.visitor_ip,
                'user_agent': session.user_agent,
                'referrer': session.referrer_url,
                'metadata': session.visitor_metadata
            }
        }
        
        return analytics
        
    except Exception as e:
        logger.error(f"Error getting analytics for session {session.session_id}: {e}")
        return {}


def cleanup_expired_sessions():
    """
    Clean up expired sessions.
    
    This function should be called periodically (e.g., via a cron job)
    to clean up old sessions and free up database space.
    
    Returns:
        dict: Cleanup statistics
    """
    from .models import WebsiteSession
    from django.utils import timezone
    
    try:
        # Find sessions that are expired (24+ hours old and inactive)
        expiry_time = timezone.now() - timezone.timedelta(hours=24)
        expired_sessions = WebsiteSession.objects.filter(
            last_activity__lt=expiry_time,
            status='active'
        )
        
        count = expired_sessions.count()
        
        # Mark as expired
        expired_sessions.update(status='expired')
        
        logger.info(f"Marked {count} sessions as expired")
        
        # Optionally delete very old sessions (30+ days)
        very_old_time = timezone.now() - timezone.timedelta(days=30)
        old_sessions = WebsiteSession.objects.filter(
            created_at__lt=very_old_time
        )
        
        deleted_count = old_sessions.count()
        old_sessions.delete()
        
        logger.info(f"Deleted {deleted_count} old sessions")
        
        return {
            'expired_count': count,
            'deleted_count': deleted_count,
            'cleanup_time': timezone.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error during session cleanup: {e}")
        return {'error': str(e)}


def validate_widget_config(config):
    """
    Validate widget configuration data.
    
    Args:
        config: Widget configuration dictionary
        
    Returns:
        tuple: (is_valid, errors)
    """
    errors = []
    
    # Required fields
    required_fields = ['primary_color', 'secondary_color', 'text_color']
    for field in required_fields:
        if field not in config:
            errors.append(f"Missing required field: {field}")
    
    # Color validation (basic hex color check)
    color_fields = ['primary_color', 'secondary_color', 'text_color', 'header_bg', 'header_text']
    for field in color_fields:
        if field in config:
            color = config[field]
            if not isinstance(color, str) or not color.startswith('#') or len(color) not in [4, 7]:
                errors.append(f"Invalid color format for {field}: {color}")
    
    # Position validation
    if 'position' in config:
        valid_positions = ['bottom-right', 'bottom-left', 'top-right', 'top-left']
        if config['position'] not in valid_positions:
            errors.append(f"Invalid position: {config['position']}. Must be one of {valid_positions}")
    
    return len(errors) == 0, errors


def get_widget_embed_code(company_slug, options=None):
    """
    Generate embed code for the widget.
    
    Args:
        company_slug: Company identifier
        options: Additional widget options
        
    Returns:
        str: HTML embed code
    """
    if options is None:
        options = {}
    
    # Base widget URL (should be configurable)
    widget_url = getattr(settings, 'WIDGET_BASE_URL', '/static/widget/widget.js')
    
    embed_code = f"""
<!-- SAIA Chatbot Widget -->
<div id="saia-widget-{company_slug}"></div>
<script>
  window.saiaWidgetConfig = {{
    company: '{company_slug}',
    apiUrl: '{settings.WIDGET_API_BASE_URL if hasattr(settings, 'WIDGET_API_BASE_URL') else '/api/widget'}',
    ...{options}
  }};
</script>
<script src="{widget_url}" async></script>
<!-- End SAIA Chatbot Widget -->
""".strip()
    
    return embed_code
