import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.auth import get_user_model
from django_ai_assistant.models import Thread
from company.models import Company

User = get_user_model()


class WebsiteSession(models.Model):
    """
    Tracks anonymous website visitor sessions for the chatbot widget.
    Each session represents a conversation between a website visitor and the AI assistant.
    """

    STATUS_CHOICES = [
        ('active', _('Active')),
        ('closed', _('Closed')),
        ('expired', _('Expired')),
    ]

    # Core session data
    session_id = models.UUIDField(
        _("Session ID"),
        unique=True,
        default=uuid.uuid4,
        help_text=_("Unique identifier for this widget session")
    )

    thread = models.OneToOneField(
        Thread,
        on_delete=models.CASCADE,
        related_name='website_session',
        help_text=_("Associated AI conversation thread")
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='website_sessions',
        help_text=_("Company whose website this session belongs to")
    )

    # Session status and timing
    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )

    created_at = models.DateTimeField(
        _("Created At"),
        auto_now_add=True
    )

    last_activity = models.DateTimeField(
        _("Last Activity"),
        auto_now=True
    )

    closed_at = models.DateTimeField(
        _("Closed At"),
        null=True,
        blank=True
    )

    # Visitor information
    visitor_ip = models.GenericIPAddressField(
        _("Visitor IP"),
        help_text=_("IP address of the website visitor")
    )

    user_agent = models.TextField(
        _("User Agent"),
        blank=True,
        help_text=_("Browser user agent string")
    )

    referrer_url = models.URLField(
        _("Referrer URL"),
        blank=True,
        help_text=_("URL that referred the visitor to the chat")
    )

    # Additional visitor metadata (JSON field for flexibility)
    visitor_metadata = models.JSONField(
        _("Visitor Metadata"),
        default=dict,
        blank=True,
        help_text=_("Additional visitor information (screen resolution, timezone, etc.)")
    )

    class Meta:
        verbose_name = _("Website Session")
        verbose_name_plural = _("Website Sessions")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['company', 'status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['visitor_ip']),
        ]

    def __str__(self):
        return f"{self.company.name} - {self.session_id}"

    @property
    def is_active(self):
        """Check if session is currently active"""
        return self.status == 'active'

    @property
    def is_expired(self):
        """Check if session has expired (24 hours of inactivity)"""
        if self.status == 'expired':
            return True

        # Auto-expire after 24 hours of inactivity
        expiry_time = timezone.now() - timezone.timedelta(hours=24)
        return self.last_activity < expiry_time

    @property
    def duration_minutes(self):
        """Get session duration in minutes"""
        end_time = self.closed_at or timezone.now()
        duration = end_time - self.created_at
        return int(duration.total_seconds() / 60)

    def close_session(self, reason=None):
        """Close the session"""
        self.status = 'closed'
        self.closed_at = timezone.now()
        self.save()

    def get_message_count(self):
        """Get total number of messages in this session"""
        return self.thread.messages.count()


class SessionHandover(models.Model):
    """
    Manages handover from AI assistant to human agents.
    Tracks when a conversation needs human intervention.
    """

    STATUS_CHOICES = [
        ('requested', _('Requested')),
        ('assigned', _('Assigned')),
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    ]

    PRIORITY_CHOICES = [
        ('low', _('Low')),
        ('medium', _('Medium')),
        ('high', _('High')),
        ('urgent', _('Urgent')),
    ]

    # Core handover data
    session = models.ForeignKey(
        WebsiteSession,
        on_delete=models.CASCADE,
        related_name='handovers',
        help_text=_("Website session requesting handover")
    )

    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=STATUS_CHOICES,
        default='requested'
    )

    priority = models.CharField(
        _("Priority"),
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium'
    )

    # Timing
    requested_at = models.DateTimeField(
        _("Requested At"),
        auto_now_add=True
    )

    assigned_at = models.DateTimeField(
        _("Assigned At"),
        null=True,
        blank=True
    )

    completed_at = models.DateTimeField(
        _("Completed At"),
        null=True,
        blank=True
    )

    # Agent assignment
    assigned_agent = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_handovers',
        help_text=_("Human agent assigned to handle this session")
    )

    # Handover details
    reason = models.TextField(
        _("Handover Reason"),
        help_text=_("Why this session needs human intervention")
    )

    notes = models.TextField(
        _("Agent Notes"),
        blank=True,
        help_text=_("Notes from the human agent")
    )

    # Customer satisfaction
    customer_rating = models.IntegerField(
        _("Customer Rating"),
        null=True,
        blank=True,
        help_text=_("Customer satisfaction rating (1-5)")
    )

    customer_feedback = models.TextField(
        _("Customer Feedback"),
        blank=True,
        help_text=_("Customer feedback about the handover experience")
    )

    class Meta:
        verbose_name = _("Session Handover")
        verbose_name_plural = _("Session Handovers")
        ordering = ['-requested_at']
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['assigned_agent', 'status']),
            models.Index(fields=['requested_at']),
        ]

    def __str__(self):
        return f"Handover for {self.session} - {self.status}"

    def assign_to_agent(self, agent):
        """Assign this handover to a human agent"""
        self.assigned_agent = agent
        self.status = 'assigned'
        self.assigned_at = timezone.now()
        self.save()

    def mark_in_progress(self):
        """Mark handover as in progress"""
        self.status = 'in_progress'
        self.save()

    def complete_handover(self, notes=None):
        """Complete the handover"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        if notes:
            self.notes = notes
        self.save()

    @property
    def response_time_minutes(self):
        """Get response time in minutes (from request to assignment)"""
        if not self.assigned_at:
            return None
        duration = self.assigned_at - self.requested_at
        return int(duration.total_seconds() / 60)

    @property
    def resolution_time_minutes(self):
        """Get total resolution time in minutes"""
        if not self.completed_at:
            return None
        duration = self.completed_at - self.requested_at
        return int(duration.total_seconds() / 60)
