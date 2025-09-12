import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django_ai_assistant.models import Thread
from company.models import Company

User = get_user_model()


class ThreadExtension(models.Model):
    """
    Extension to the django_ai_assistant Thread model for website chatbot functionality.

    This model extends the base Thread model with additional fields needed for
    multi-tenant website chatbot sessions without modifying the core library.
    """

    thread = models.OneToOneField(
        Thread,
        on_delete=models.CASCADE,
        related_name='chatbot_extension',
        help_text=_("Reference to the base Thread model")
    )

    # Session Type Differentiation
    SESSION_TYPE_CHOICES = [
        ('admin', _('Admin Chat')),
        ('website', _('Website Chat')),
    ]

    session_type = models.CharField(
        _("Session Type"),
        max_length=20,
        choices=SESSION_TYPE_CHOICES,
        default='admin',
        help_text=_("Type of chat session (admin vs website)")
    )

    # Anonymous Session Support
    is_anonymous = models.BooleanField(
        _("Is Anonymous"),
        default=False,
        help_text=_("Whether this is an anonymous visitor session")
    )

    # Visitor Metadata (for anonymous sessions)
    visitor_metadata = models.JSONField(
        _("Visitor Metadata"),
        default=dict,
        blank=True,
        help_text=_("Additional visitor information for anonymous sessions")
    )

    # Timestamps
    created_at = models.DateTimeField(
        _("Created At"),
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        _("Updated At"),
        auto_now=True
    )

    class Meta:
        verbose_name = _("Thread Extension")
        verbose_name_plural = _("Thread Extensions")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['session_type']),
            models.Index(fields=['is_anonymous']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.thread.name} - {self.get_session_type_display()}"

    @property
    def is_website_session(self):
        """Check if this is a website chat session"""
        return self.session_type == 'website'

    @property
    def is_admin_session(self):
        """Check if this is an admin chat session"""
        return self.session_type == 'admin'


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
        help_text=_("Company this configuration belongs to")
    )

    # Widget Appearance
    theme_config = models.JSONField(
        _("Theme Configuration"),
        default=dict,
        help_text=_("Theme configuration (colors, fonts, etc.)")
    )

    welcome_message = models.TextField(
        _("Welcome Message"),
        default="Hello! How can we help you today?",
        help_text=_("Initial message shown to website visitors")
    )

    # Widget Behavior
    position = models.CharField(
        _("Widget Position"),
        max_length=20,
        choices=[
            ('bottom-right', _('Bottom Right')),
            ('bottom-left', _('Bottom Left')),
            ('top-right', _('Top Right')),
            ('top-left', _('Top Left')),
        ],
        default='bottom-right',
        help_text=_("Position of the widget on the website")
    )

    auto_open = models.BooleanField(
        _("Auto Open"),
        default=False,
        help_text=_("Whether to automatically open the widget")
    )

    auto_open_delay = models.IntegerField(
        _("Auto Open Delay"),
        default=3,
        validators=[MinValueValidator(0), MaxValueValidator(60)],
        help_text=_("Delay in seconds before auto-opening (0-60)")
    )

    # Security & Rate Limiting
    rate_limit_per_minute = models.IntegerField(
        _("Rate Limit Per Minute"),
        default=20,
        validators=[MinValueValidator(1), MaxValueValidator(1000)],
        help_text=_("Maximum messages per minute per visitor")
    )

    max_message_length = models.IntegerField(
        _("Max Message Length"),
        default=2000,
        validators=[MinValueValidator(100), MaxValueValidator(10000)],
        help_text=_("Maximum length of a single message")
    )

    # File Upload Settings
    allowed_file_types = models.JSONField(
        _("Allowed File Types"),
        default=list,
        help_text=_("List of allowed file extensions (e.g., ['pdf', 'jpg', 'png'])")
    )

    max_file_size_mb = models.IntegerField(
        _("Max File Size (MB)"),
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(50)],
        help_text=_("Maximum file size in megabytes")
    )

    # Widget Status
    is_active = models.BooleanField(
        _("Is Active"),
        default=True,
        help_text=_("Whether the widget is active and visible")
    )

    # Timestamps
    created_at = models.DateTimeField(
        _("Created At"),
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        _("Updated At"),
        auto_now=True
    )

    class Meta:
        verbose_name = _("Widget Configuration")
        verbose_name_plural = _("Widget Configurations")
        ordering = ['company__name']

    def __str__(self):
        return f"{self.company.name} - Widget Config"

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
        return f"{base_url}/static/widget/js/saia-widget.js"

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
