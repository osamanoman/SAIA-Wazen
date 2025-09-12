"""
Public API endpoints for SAIA Multi-Tenant Website Chatbot Platform

These endpoints are designed to be called from the website widget without authentication.
They handle anonymous visitor sessions and company-specific AI assistant routing.
"""

import uuid
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
from django.db import transaction

from ninja import NinjaAPI, Schema, Field
from ninja.errors import HttpError

from company.models import Company
from django_ai_assistant.models import Thread as BaseThread, Message as BaseMessage
from django_ai_assistant.helpers.use_cases import create_message


from .models import WebsiteSession, WidgetConfiguration, ThreadExtension
from .helpers import create_website_thread, get_company_widget_config, close_expired_sessions

logger = logging.getLogger(__name__)

# Create public API instance (no authentication required)
widget_api = NinjaAPI(
    title="SAIA Widget API",
    version="1.0.0",
    description="Public API for SAIA website chatbot widgets",
    urls_namespace="widget",
    csrf=False,  # Disable CSRF for public API
)


# ==================== SCHEMAS ====================

class WidgetConfigResponse(Schema):
    """Widget configuration response schema"""
    company_name: str
    welcome_message: str
    theme_config: Dict[str, Any]
    position: str
    auto_open: bool
    auto_open_delay: int
    is_active: bool


class SessionCreateRequest(Schema):
    """Request schema for creating a new website session"""
    company_slug: str = Field(..., description="Company identifier (slug)")
    visitor_ip: Optional[str] = Field(None, description="Visitor IP address")
    user_agent: Optional[str] = Field(None, description="Browser user agent")
    referrer_url: Optional[str] = Field(None, description="Referrer URL")
    visitor_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional visitor data")


class SessionCreateResponse(Schema):
    """Response schema for session creation"""
    session_id: str
    company_name: str
    assistant_id: str
    welcome_message: str
    theme_config: Dict[str, Any]


class MessageSendRequest(Schema):
    """Request schema for sending a message"""
    content: str = Field(..., min_length=1, max_length=2000, description="Message content")
    message_type: str = Field(default="human", description="Message type")


class MessageResponse(Schema):
    """Response schema for messages"""
    id: str
    content: str
    message_type: str
    timestamp: datetime
    is_ai: bool


class SessionStatusResponse(Schema):
    """Response schema for session status"""
    session_id: str
    status: str
    is_active: bool
    message_count: int
    duration_minutes: int
    last_activity: datetime


# ==================== UTILITY FUNCTIONS ====================

def get_client_ip(request: HttpRequest) -> str:
    """Extract client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
    return ip


def validate_company_slug(company_slug: str) -> Company:
    """Validate and get company by slug"""
    try:
        # Try exact match first
        return Company.objects.get(name__iexact=company_slug)
    except Company.DoesNotExist:
        # Try slug-like matching (replace hyphens with spaces)
        company_name = company_slug.replace('-', ' ').replace('_', ' ')
        try:
            return Company.objects.get(name__icontains=company_name)
        except Company.DoesNotExist:
            raise HttpError(404, f"Company '{company_slug}' not found")


# ==================== API ENDPOINTS ====================

@widget_api.get("/config/{company_slug}/", response=WidgetConfigResponse)
def get_widget_config(request: HttpRequest, company_slug: str):
    """
    Get widget configuration for a company.
    
    This endpoint provides the widget with company-specific configuration
    including theme, welcome message, and behavior settings.
    """
    try:
        company = validate_company_slug(company_slug)
        config = get_company_widget_config(company)
        
        if not config.is_active:
            raise HttpError(403, "Widget is not active for this company")
        
        return WidgetConfigResponse(
            company_name=company.name,
            welcome_message=config.welcome_message,
            theme_config=config.get_theme_config(),
            position=config.position,
            auto_open=config.auto_open,
            auto_open_delay=config.auto_open_delay,
            is_active=config.is_active
        )
        
    except Exception as e:
        logger.error(f"Error getting widget config for {company_slug}: {e}")
        raise HttpError(500, "Internal server error")


@widget_api.post("/session/create/", response=SessionCreateResponse)
def create_session(request: HttpRequest, data: SessionCreateRequest):
    """
    Create a new website chat session for an anonymous visitor.
    
    This endpoint creates a new thread and session for a website visitor,
    automatically routing to the company's specific AI assistant.
    """
    try:
        with transaction.atomic():
            # Validate company
            company = validate_company_slug(data.company_slug)
            
            # Get widget configuration
            config = get_company_widget_config(company)
            if not config.is_active:
                raise HttpError(403, "Chat widget is not active for this company")
            
            # Get visitor IP if not provided
            visitor_ip = data.visitor_ip or get_client_ip(request)
            
            # Create website thread and session
            thread, website_session = create_website_thread(
                company=company,
                visitor_ip=visitor_ip,
                user_agent=data.user_agent or request.META.get('HTTP_USER_AGENT', ''),
                referrer_url=data.referrer_url or '',
                visitor_metadata=data.visitor_metadata
            )
            
            logger.info(f"Created website session {website_session.session_id} for {company.name}")
            
            return SessionCreateResponse(
                session_id=str(website_session.session_id),
                company_name=company.name,
                assistant_id=thread.assistant_id,
                welcome_message=config.welcome_message,
                theme_config=config.get_theme_config()
            )
            
    except HttpError:
        raise
    except Exception as e:
        logger.error(f"Error creating session for {data.company_slug}: {e}")
        raise HttpError(500, "Failed to create chat session")


@widget_api.post("/session/{session_id}/send/", response=MessageResponse)
def send_message(request: HttpRequest, session_id: str, data: MessageSendRequest):
    """
    Send a message to a website chat session.
    
    This endpoint handles visitor messages and generates AI responses
    using the company's specific AI assistant.
    """
    try:
        with transaction.atomic():
            # Get website session
            try:
                session_uuid = uuid.UUID(session_id)
                website_session = get_object_or_404(
                    WebsiteSession.objects.select_related('thread', 'company'),
                    session_id=session_uuid
                )
            except ValueError:
                raise HttpError(400, "Invalid session ID format")
            
            # Check if session is active
            if not website_session.is_active():
                raise HttpError(400, "Chat session is not active")
            
            # Check if session is expired
            if website_session.is_expired():
                website_session.close_session(reason='timeout')
                raise HttpError(400, "Chat session has expired")
            
            # Update last activity
            website_session.last_activity = timezone.now()
            website_session.save(update_fields=['last_activity'])
            
            # Send message to AI assistant
            thread = website_session.thread

            # Send message and get AI response using create_message
            ai_response = create_message(
                assistant_id=thread.assistant_id,
                thread=thread,
                user=None,  # Anonymous user
                content=data.content,
                request=request
            )
            
            # Get the latest AI message
            latest_message = thread.messages.order_by('-created_at').first()
            
            if latest_message:
                message_data = latest_message.message
                return MessageResponse(
                    id=str(latest_message.id),
                    content=message_data.get('content', ''),
                    message_type=message_data.get('type', 'ai'),
                    timestamp=latest_message.created_at,
                    is_ai=True
                )
            else:
                raise HttpError(500, "Failed to get AI response")
                
    except HttpError:
        raise
    except Exception as e:
        logger.error(f"Error sending message to session {session_id}: {e}")
        raise HttpError(500, "Failed to send message")


@widget_api.get("/session/{session_id}/messages/", response=List[MessageResponse])
def get_messages(request: HttpRequest, session_id: str, limit: int = 50):
    """
    Get message history for a website chat session.
    
    This endpoint returns the conversation history for a session,
    useful for restoring chat state after page reload.
    """
    try:
        # Get website session
        try:
            session_uuid = uuid.UUID(session_id)
            website_session = get_object_or_404(
                WebsiteSession.objects.select_related('thread'),
                session_id=session_uuid
            )
        except ValueError:
            raise HttpError(400, "Invalid session ID format")
        
        # Get messages from thread
        messages = website_session.thread.messages.order_by('created_at')[:limit]
        
        response_messages = []
        for message in messages:
            message_data = message.message
            message_type = message_data.get('type', 'unknown')
            
            response_messages.append(MessageResponse(
                id=str(message.id),
                content=message_data.get('content', ''),
                message_type=message_type,
                timestamp=message.created_at,
                is_ai=message_type in ['ai', 'assistant']
            ))
        
        return response_messages
        
    except HttpError:
        raise
    except Exception as e:
        logger.error(f"Error getting messages for session {session_id}: {e}")
        raise HttpError(500, "Failed to get messages")


@widget_api.get("/session/{session_id}/status/", response=SessionStatusResponse)
def get_session_status(request: HttpRequest, session_id: str):
    """
    Get status information for a website chat session.
    
    This endpoint provides session metadata including status,
    message count, and duration.
    """
    try:
        # Get website session
        try:
            session_uuid = uuid.UUID(session_id)
            website_session = get_object_or_404(WebsiteSession, session_id=session_uuid)
        except ValueError:
            raise HttpError(400, "Invalid session ID format")
        
        return SessionStatusResponse(
            session_id=session_id,
            status=website_session.status,
            is_active=website_session.is_active(),
            message_count=website_session.get_message_count(),
            duration_minutes=website_session.get_duration_minutes(),
            last_activity=website_session.last_activity
        )
        
    except HttpError:
        raise
    except Exception as e:
        logger.error(f"Error getting status for session {session_id}: {e}")
        raise HttpError(500, "Failed to get session status")


@widget_api.put("/session/{session_id}/close/")
def close_session(request: HttpRequest, session_id: str):
    """
    Close a website chat session.
    
    This endpoint allows the widget to explicitly close a session
    when the visitor leaves or closes the chat.
    """
    try:
        # Get website session
        try:
            session_uuid = uuid.UUID(session_id)
            website_session = get_object_or_404(WebsiteSession, session_id=session_uuid)
        except ValueError:
            raise HttpError(400, "Invalid session ID format")
        
        if website_session.is_active():
            website_session.close_session(reason='user_closed')
            logger.info(f"Closed website session {session_id}")
        
        return {"message": "Session closed successfully"}
        
    except HttpError:
        raise
    except Exception as e:
        logger.error(f"Error closing session {session_id}: {e}")
        raise HttpError(500, "Failed to close session")


# ==================== MAINTENANCE ENDPOINTS ====================

@widget_api.post("/maintenance/cleanup-expired/")
def cleanup_expired_sessions(request: HttpRequest, timeout_minutes: int = 30):
    """
    Cleanup expired website sessions.
    
    This endpoint can be called periodically to close sessions
    that have been inactive for too long.
    """
    try:
        closed_count = close_expired_sessions(timeout_minutes)
        logger.info(f"Closed {closed_count} expired sessions")
        
        return {
            "message": f"Cleaned up {closed_count} expired sessions",
            "closed_count": closed_count
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up expired sessions: {e}")
        raise HttpError(500, "Failed to cleanup expired sessions")
