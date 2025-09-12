"""
Helper functions for SAIA Multi-Tenant Website Chatbot Platform
"""

import uuid
from typing import Optional, Dict, Any
from django.contrib.auth import get_user_model
from django.utils import timezone

from django_ai_assistant.models import Thread as BaseThread
from company.models import Company
from .models import ThreadExtension, WebsiteSession, WidgetConfiguration

User = get_user_model()


def create_website_thread(
    company: Company,
    visitor_ip: str,
    user_agent: str = '',
    referrer_url: str = '',
    visitor_metadata: Optional[Dict[str, Any]] = None
) -> tuple[BaseThread, WebsiteSession]:
    """
    Create a new website chat thread for anonymous visitors.
    
    Args:
        company: Company the visitor is chatting with
        visitor_ip: IP address of the visitor
        user_agent: Browser user agent string
        referrer_url: URL that referred the visitor
        visitor_metadata: Additional visitor information
    
    Returns:
        tuple: (Thread, WebsiteSession) objects
    """
    
    # Get company's AI assistant ID
    assistant_id = company.get_company_assistant_id()
    if not assistant_id:
        # Fallback to default company assistant naming
        assistant_id = f"{company.name.lower().replace(' ', '_')}_ai_assistant"
    
    # Create thread name
    thread_name = f"{company.name} Website Visitor {uuid.uuid4().hex[:8]}"
    
    # Create the base thread (anonymous, no user)
    thread = BaseThread.objects.create(
        name=thread_name,
        created_by=None,  # Anonymous visitor
        assistant_id=assistant_id
    )
    
    # Create thread extension for website session
    ThreadExtension.objects.create(
        thread=thread,
        session_type='website',
        is_anonymous=True,
        visitor_metadata=visitor_metadata or {}
    )
    
    # Create website session
    website_session = WebsiteSession.objects.create(
        session_id=uuid.uuid4(),
        thread=thread,
        company=company,
        visitor_ip=visitor_ip,
        user_agent=user_agent,
        referrer_url=referrer_url,
        visitor_metadata=visitor_metadata or {}
    )
    
    return thread, website_session


def create_admin_thread(
    user: User,
    company: Company,
    thread_name: str = '',
    assistant_id: str = ''
) -> BaseThread:
    """
    Create a new admin chat thread for authenticated users.
    
    Args:
        user: Authenticated user creating the thread
        company: User's company
        thread_name: Custom thread name (optional)
        assistant_id: Specific assistant ID (optional)
    
    Returns:
        Thread: Created thread object
    """
    
    # Generate thread name if not provided
    if not thread_name:
        thread_name = f"{company.name} Admin Chat {timezone.now().strftime('%Y-%m-%d %H:%M')}"
    
    # Get assistant ID if not provided
    if not assistant_id:
        assistant_id = company.get_company_assistant_id()
        if not assistant_id:
            assistant_id = f"{company.name.lower().replace(' ', '_')}_ai_assistant"
    
    # Create the base thread
    thread = BaseThread.objects.create(
        name=thread_name,
        created_by=user,
        assistant_id=assistant_id
    )
    
    # Create thread extension for admin session
    ThreadExtension.objects.create(
        thread=thread,
        session_type='admin',
        is_anonymous=False,
        visitor_metadata={}
    )
    
    return thread


def get_company_widget_config(company: Company) -> WidgetConfiguration:
    """
    Get or create widget configuration for a company.
    
    Args:
        company: Company to get configuration for
    
    Returns:
        WidgetConfiguration: Widget configuration object
    """
    
    config, created = WidgetConfiguration.objects.get_or_create(
        company=company,
        defaults={
            'welcome_message': f"Hello! How can {company.name} help you today?",
            'theme_config': {
                'primary_color': '#1e40af',
                'secondary_color': '#f3f4f6',
                'text_color': '#1f2937',
                'header_bg': '#1e40af',
                'header_text': '#ffffff',
            },
            'position': 'bottom-right',
            'auto_open': False,
            'auto_open_delay': 3,
            'is_active': True
        }
    )
    
    return config


def is_website_thread(thread: BaseThread) -> bool:
    """
    Check if a thread is a website chat thread.
    
    Args:
        thread: Thread to check
    
    Returns:
        bool: True if website thread, False otherwise
    """
    try:
        extension = thread.chatbot_extension
        return extension.session_type == 'website'
    except ThreadExtension.DoesNotExist:
        return False


def is_anonymous_thread(thread: BaseThread) -> bool:
    """
    Check if a thread is for an anonymous visitor.
    
    Args:
        thread: Thread to check
    
    Returns:
        bool: True if anonymous thread, False otherwise
    """
    try:
        extension = thread.chatbot_extension
        return extension.is_anonymous
    except ThreadExtension.DoesNotExist:
        return False


def get_thread_company(thread: BaseThread) -> Optional[Company]:
    """
    Get the company associated with a thread.
    
    Args:
        thread: Thread to get company for
    
    Returns:
        Company: Associated company or None
    """
    try:
        # Try website session first
        if hasattr(thread, 'website_session'):
            return thread.website_session.company
        
        # Try user's company for admin threads
        if thread.created_by and hasattr(thread.created_by, 'company'):
            return thread.created_by.company
        
        return None
    except Exception:
        return None


def get_active_website_sessions(company: Company) -> 'QuerySet[WebsiteSession]':
    """
    Get active website sessions for a company.
    
    Args:
        company: Company to get sessions for
    
    Returns:
        QuerySet: Active website sessions
    """
    return WebsiteSession.objects.filter(
        company=company,
        status='active'
    ).select_related('thread').order_by('-last_activity')


def get_expired_website_sessions(timeout_minutes: int = 30) -> 'QuerySet[WebsiteSession]':
    """
    Get expired website sessions that should be closed.
    
    Args:
        timeout_minutes: Session timeout in minutes
    
    Returns:
        QuerySet: Expired website sessions
    """
    timeout_time = timezone.now() - timezone.timedelta(minutes=timeout_minutes)
    
    return WebsiteSession.objects.filter(
        status='active',
        last_activity__lt=timeout_time
    )


def close_expired_sessions(timeout_minutes: int = 30) -> int:
    """
    Close expired website sessions.
    
    Args:
        timeout_minutes: Session timeout in minutes
    
    Returns:
        int: Number of sessions closed
    """
    expired_sessions = get_expired_website_sessions(timeout_minutes)
    count = expired_sessions.count()
    
    for session in expired_sessions:
        session.close_session(reason='timeout')
    
    return count
