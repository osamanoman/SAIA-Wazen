"""
Helper functions for SAIA Multi-Tenant Website Chatbot Widget

This module contains utility functions for managing website chat sessions,
thread creation, and company-specific configurations.
"""

import uuid
from typing import Dict, Any, Optional, List
from django.utils import timezone
from django.contrib.auth import get_user_model
from django_ai_assistant.models import Thread as BaseThread

from company.models import Company
from .models import WebsiteSession, ThreadExtension, WidgetConfiguration

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

    # Create or get anonymous user for this company
    anonymous_username = f'widget_anonymous_{company.name.lower()}'
    anonymous_user, created = User.objects.get_or_create(
        username=anonymous_username,
        defaults={
            'email': f'anonymous@{company.name.lower()}.widget',
            'first_name': 'Anonymous',
            'last_name': f'{company.name} Widget User',
            'is_active': True,
            'is_staff': False,
            'is_superuser': False,
            'is_customer': True,  # Mark as customer user
            'company': company
        }
    )

    # Create the base thread with anonymous user as creator
    thread = BaseThread.objects.create(
        name=thread_name,
        created_by=anonymous_user,  # Use anonymous user as creator
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
    
    # Create the thread
    thread = BaseThread.objects.create(
        name=thread_name,
        created_by=user,
        assistant_id=assistant_id
    )
    
    # Create thread extension for admin session
    ThreadExtension.objects.create(
        thread=thread,
        session_type='admin',
        is_anonymous=False
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
            'is_active': True,
            'rate_limit_per_minute': 20,
            'max_message_length': 2000,
            'allowed_file_types': ['pdf', 'jpg', 'jpeg', 'png', 'gif', 'txt'],
            'max_file_size_mb': 5
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


def get_active_website_sessions(company: Company = None) -> List[WebsiteSession]:
    """
    Get all active website sessions, optionally filtered by company.
    
    Args:
        company: Optional company filter
    
    Returns:
        List[WebsiteSession]: Active sessions
    """
    queryset = WebsiteSession.objects.filter(status='active')
    
    if company:
        queryset = queryset.filter(company=company)
    
    return queryset.select_related('company', 'thread').order_by('-last_activity')


def get_expired_website_sessions(timeout_minutes: int = 30) -> List[WebsiteSession]:
    """
    Get expired website sessions based on inactivity timeout.
    
    Args:
        timeout_minutes: Session timeout in minutes
    
    Returns:
        List[WebsiteSession]: Expired sessions
    """
    cutoff_time = timezone.now() - timezone.timedelta(minutes=timeout_minutes)
    
    return WebsiteSession.objects.filter(
        status='active',
        last_activity__lt=cutoff_time
    ).select_related('company', 'thread')


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
        session.close_session()
    
    return count


def get_company_by_slug(company_slug: str) -> Optional[Company]:
    """
    Get company by slug (name converted to lowercase with spaces replaced by hyphens).

    Args:
        company_slug: Company slug (e.g., 'wazen', 'my-company')

    Returns:
        Company: Company object or None
    """
    try:
        # Convert slug back to potential company name
        potential_name = company_slug.replace('-', ' ').replace('_', ' ')

        # Try exact case-insensitive match first
        return Company.objects.get(name__iexact=potential_name)
    except Company.DoesNotExist:
        # Try partial case-insensitive match
        try:
            return Company.objects.get(name__icontains=potential_name)
        except Company.DoesNotExist:
            # Try with original slug as-is
            try:
                return Company.objects.get(name__iexact=company_slug)
            except Company.DoesNotExist:
                return None
