"""
Chatbot Models for SAIA Multi-Tenant Website Chatbot Platform

This module contains all models related to the website chatbot functionality,
including session tracking, handover management, and widget configuration.
"""

import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

from company.models import Company
from django_ai_assistant.models import Thread as BaseThread

User = get_user_model()


class ThreadExtension(models.Model):
    """
    Extension to the django_ai_assistant Thread model for website chatbot functionality.

    This model extends the base Thread model with additional fields needed for
    multi-tenant website chatbot sessions without modifying the core library.
    """

    thread = models.OneToOneField(
        BaseThread,
        on_delete=models.CASCADE,
        related_name='chatbot_extension',
        help_text="Reference to the base Thread model"
    )

    # Session Type Differentiation
    SESSION_TYPE_CHOICES = [
        ('admin', 'Admin Chat'),
        ('website', 'Website Chat'),
    ]

    session_type = models.CharField(
        max_length=20,
        choices=SESSION_TYPE_CHOICES,
        default='admin',
        help_text="Type of chat session (admin vs website)"
    )

    # Anonymous Session Support
    is_anonymous = models.BooleanField(
        default=False,
        help_text="Whether this is an anonymous website visitor session"
    )

    # Visitor Metadata for Anonymous Sessions
    visitor_metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional metadata for anonymous website visitors"
    )

    class Meta:
        db_table = 'chatbot_thread_extensions'
        verbose_name = 'Thread Extension'
        verbose_name_plural = 'Thread Extensions'

        indexes = [
            models.Index(fields=['session_type'], name='chatbot_thread_type_idx'),
            models.Index(fields=['is_anonymous'], name='chatbot_thread_anon_idx'),
        ]

    def __str__(self):
        return f"Extension for Thread {self.thread.id} ({self.session_type})"

    @classmethod
    def get_or_create_for_thread(cls, thread, session_type='admin', is_anonymous=False, visitor_metadata=None):
        """Get or create extension for a thread"""
        extension, created = cls.objects.get_or_create(
            thread=thread,
            defaults={
                'session_type': session_type,
                'is_anonymous': is_anonymous,
                'visitor_metadata': visitor_metadata or {}
            }
        )
        return extension, created


class WebsiteSession(models.Model):
    """
    Track anonymous website visitors and their chat sessions.
    
    This model provides complete isolation between companies while
    enabling tracking of anonymous website visitors without requiring
    user accounts.
    """
    
    # Session Management
    session_id = models.UUIDField(
        unique=True, 
        default=uuid.uuid4,
        help_text="Unique identifier for the website visitor session"
    )
    
    thread = models.OneToOneField(
        BaseThread,
        on_delete=models.CASCADE,
        related_name='website_session',
        help_text="Associated conversation thread"
    )
    
    # Company Isolation
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='website_sessions',
        help_text="Company this session belongs to (for data isolation)"
    )
    
    # Visitor Information
    visitor_ip = models.GenericIPAddressField(
        help_text="IP address of the website visitor"
    )
    
    user_agent = models.TextField(
        blank=True,
        help_text="Browser user agent string"
    )
    
    referrer_url = models.URLField(
        blank=True,
        null=True,
        help_text="URL that referred the visitor to the chat"
    )
    
    # Session Status
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('closed', 'Closed'),
        ('handover', 'Agent Handover'),
        ('archived', 'Archived'),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        help_text="Current status of the chat session"
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the session was created"
    )
    
    last_activity = models.DateTimeField(
        auto_now=True,
        help_text="Last activity timestamp (updated on each message)"
    )
    
    closed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the session was closed"
    )
    
    # Visitor Metadata (JSON field for flexible data storage)
    visitor_metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional visitor information (browser, screen size, etc.)"
    )
    
    class Meta:
        db_table = 'chatbot_website_sessions'
        verbose_name = 'Website Chat Session'
        verbose_name_plural = 'Website Chat Sessions'
        ordering = ['-last_activity']
        
        indexes = [
            models.Index(fields=['company', 'status'], name='chatbot_company_status_idx'),
            models.Index(fields=['created_at'], name='chatbot_created_at_idx'),
            models.Index(fields=['last_activity'], name='chatbot_last_activity_idx'),
            models.Index(fields=['session_id'], name='chatbot_session_id_idx'),
        ]
    
    def __str__(self):
        return f"{self.company.name} - Session {self.session_id.hex[:8]} ({self.status})"
    
    def is_active(self):
        """Check if session is currently active"""
        return self.status == 'active'
    
    def is_expired(self, timeout_minutes=30):
        """Check if session has expired due to inactivity"""
        if self.status != 'active':
            return False
        
        timeout_delta = timezone.timedelta(minutes=timeout_minutes)
        return timezone.now() - self.last_activity > timeout_delta
    
    def close_session(self, reason='completed'):
        """Close the session and update timestamps"""
        self.status = 'closed'
        self.closed_at = timezone.now()
        self.visitor_metadata['close_reason'] = reason
        self.save(update_fields=['status', 'closed_at', 'visitor_metadata'])
    
    def get_message_count(self):
        """Get total number of messages in this session"""
        return self.thread.messages.count()
    
    def get_duration_minutes(self):
        """Get session duration in minutes"""
        end_time = self.closed_at or timezone.now()
        duration = end_time - self.created_at
        return int(duration.total_seconds() / 60)


class SessionHandover(models.Model):
    """
    Manage agent handover workflow for website chat sessions.
    
    When a website visitor needs human assistance, this model tracks
    the handover process and agent assignment.
    """
    
    website_session = models.ForeignKey(
        WebsiteSession,
        on_delete=models.CASCADE,
        related_name='handovers',
        help_text="Website session being handed over to an agent"
    )
    
    agent = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='chat_handovers',
        help_text="Support agent handling the handover"
    )
    
    # Handover Details
    handover_reason = models.TextField(
        help_text="Reason for handover (e.g., complex query, customer request)"
    )
    
    handover_trigger = models.CharField(
        max_length=50,
        choices=[
            ('ai_escalation', 'AI Escalation'),
            ('customer_request', 'Customer Request'),
            ('agent_initiated', 'Agent Initiated'),
            ('timeout', 'Session Timeout'),
        ],
        default='ai_escalation',
        help_text="What triggered the handover"
    )
    
    # Status Tracking
    STATUS_CHOICES = [
        ('pending', 'Pending Agent Response'),
        ('active', 'Agent Active'),
        ('resolved', 'Resolved'),
        ('escalated', 'Escalated Further'),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Current handover status"
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When handover was initiated"
    )
    
    agent_joined_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When agent joined the conversation"
    )
    
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When handover was resolved"
    )
    
    # Resolution Details
    resolution_notes = models.TextField(
        blank=True,
        help_text="Agent notes about the resolution"
    )
    
    customer_satisfaction = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Customer satisfaction rating (1-5)"
    )
    
    class Meta:
        db_table = 'chatbot_session_handovers'
        verbose_name = 'Session Handover'
        verbose_name_plural = 'Session Handovers'
        ordering = ['-created_at']
        
        indexes = [
            models.Index(fields=['website_session', 'status'], name='chatbot_handover_sess_idx'),
            models.Index(fields=['agent', 'status'], name='chatbot_handover_agent_idx'),
            models.Index(fields=['created_at'], name='chatbot_handover_date_idx'),
        ]
    
    def __str__(self):
        return f"Handover {self.id} - {self.website_session.company.name} to {self.agent.username}"
    
    def mark_agent_joined(self):
        """Mark that agent has joined the conversation"""
        self.status = 'active'
        self.agent_joined_at = timezone.now()
        self.save(update_fields=['status', 'agent_joined_at'])
    
    def resolve_handover(self, notes='', satisfaction=None):
        """Mark handover as resolved"""
        self.status = 'resolved'
        self.resolved_at = timezone.now()
        self.resolution_notes = notes
        if satisfaction:
            self.customer_satisfaction = satisfaction
        self.save(update_fields=['status', 'resolved_at', 'resolution_notes', 'customer_satisfaction'])
    
    def get_response_time_minutes(self):
        """Get time between handover creation and agent joining"""
        if not self.agent_joined_at:
            return None
        duration = self.agent_joined_at - self.created_at
        return int(duration.total_seconds() / 60)
    
    def get_resolution_time_minutes(self):
        """Get total time to resolve the handover"""
        if not self.resolved_at:
            return None
        duration = self.resolved_at - self.created_at
        return int(duration.total_seconds() / 60)


class WidgetConfiguration(models.Model):
    """
    Store company-specific widget customization settings.
    
    This model allows each company to customize their chatbot widget
    appearance, behavior, and branding.
    """
    
    company = models.OneToOneField(
        Company,
        on_delete=models.CASCADE,
        related_name='widget_config',
        help_text="Company this configuration belongs to"
    )
    
    # Widget Appearance
    theme_config = models.JSONField(
        default=dict,
        help_text="Theme configuration (colors, fonts, etc.)"
    )
    
    welcome_message = models.TextField(
        default="Hello! How can we help you today?",
        help_text="Initial message shown to website visitors"
    )
    
    # Widget Behavior
    position = models.CharField(
        max_length=20,
        choices=[
            ('bottom-right', 'Bottom Right'),
            ('bottom-left', 'Bottom Left'),
            ('top-right', 'Top Right'),
            ('top-left', 'Top Left'),
            ('custom', 'Custom Position'),
        ],
        default='bottom-right',
        help_text="Widget position on the website"
    )
    
    auto_open = models.BooleanField(
        default=False,
        help_text="Automatically open widget when page loads"
    )
    
    auto_open_delay = models.IntegerField(
        default=3,
        validators=[MinValueValidator(0), MaxValueValidator(60)],
        help_text="Delay in seconds before auto-opening (if enabled)"
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the widget is active on the website"
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When configuration was created"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When configuration was last updated"
    )
    
    class Meta:
        db_table = 'chatbot_widget_configurations'
        verbose_name = 'Widget Configuration'
        verbose_name_plural = 'Widget Configurations'
    
    def __str__(self):
        return f"Widget Config - {self.company.name}"
    
    def get_theme_config(self):
        """Get theme configuration with defaults"""
        default_theme = {
            'primary_color': '#1e40af',
            'secondary_color': '#f3f4f6',
            'text_color': '#1f2937',
            'header_bg': '#1e40af',
            'header_text': '#ffffff',
            'font_family': 'system-ui, -apple-system, sans-serif',
            'border_radius': '8px',
            'shadow': '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
        }
        
        # Merge with custom theme config
        theme = default_theme.copy()
        theme.update(self.theme_config)
        return theme
    
    def get_widget_script_url(self):
        """Get the widget script URL for this company"""
        from django.conf import settings
        base_url = getattr(settings, 'WIDGET_BASE_URL', 'https://your-domain.com')
        return f"{base_url}/static/widget/chatbot.js"
    
    def generate_embed_code(self):
        """Generate HTML embed code for this widget"""
        script_url = self.get_widget_script_url()
        
        embed_code = f'''<!-- SAIA Chatbot Widget -->
<div id="saia-chatbot-{self.company.id}"></div>
<script src="{script_url}"></script>
<script>
new SAIAChatWidget({{
    container: '#saia-chatbot-{self.company.id}',
    company: '{self.company.name.lower().replace(" ", "-")}',
    companyId: {self.company.id},
    theme: {self.get_theme_config()},
    welcomeMessage: '{self.welcome_message}',
    position: '{self.position}',
    autoOpen: {str(self.auto_open).lower()},
    autoOpenDelay: {self.auto_open_delay}
}});
</script>'''
        
        return embed_code
