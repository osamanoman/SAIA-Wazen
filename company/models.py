from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

# Create your models here.
ENABLED = "1"
DISABLED = "0"


class Company(models.Model):
    COMMERCIAL = "CR"
    SERVICE = "SR"

    ACTIVITY_TYPE_CHOICES = {
        COMMERCIAL: _("Commercial"),
        SERVICE: _("Service")
    }
    ACTIVITY_STATUS_CHOICES = {
        ENABLED: _("Enabled"),
        DISABLED: _("Disabled"),
    }
    name = models.CharField(_("Name"), max_length=50)
    email = models.EmailField(_("Email"), blank=True, null=True)
    phone = models.IntegerField(_("Phone"), blank=True, null=True)
    activity_name = models.CharField(_("Activity Name"), max_length=255)
    activity_type = models.CharField(_("Activity Type"), max_length=2, choices=ACTIVITY_TYPE_CHOICES)
    activity_status = models.CharField(_("Activity Status"), max_length=1, choices=ACTIVITY_STATUS_CHOICES, default=ENABLED)
    subscription_start_date = models.DateField(_("Subscription Start Date"))
    subscription_end_date = models.DateField(_("Subscription End Date"))
    subscription_status = models.CharField(_("Subscription Status"), max_length=1, choices=ACTIVITY_STATUS_CHOICES, default=ENABLED)

    # ==================== AI ASSISTANT CONFIGURATION ====================
    # These fields allow customizing the AI assistant behavior per company

    AI_LANGUAGE_CHOICES = [
        ('en', _('English')),
        ('ar', _('Arabic')),
    ]

    ai_instructions_template = models.TextField(
        _("AI Instructions Template"),
        blank=True, null=True,
        help_text=_("Custom AI instructions for this company's assistant. Leave blank to use default instructions.")
    )

    enabled_tools_json = models.JSONField(
        _("Enabled AI Tools"),
        default=list, blank=True,
        help_text=_("List of AI tools enabled for this company. Example: [\"sales_analysis\", \"inventory_check\"]. Leave empty to enable all tools.")
    )

    database_config_json = models.JSONField(
        _("Database Configuration"),
        default=dict, blank=True,
        help_text=_("Custom database connection settings for this company. Example: {\"host\": \"db.company.com\", \"name\": \"company_db\"}. Leave empty to use default connection.")
    )

    ai_language = models.CharField(
        _("AI Language"),
        max_length=10,
        choices=AI_LANGUAGE_CHOICES,
        default='en',
        help_text=_("Preferred language for AI assistant responses.")
    )

    ai_temperature = models.FloatField(
        _("AI Creativity Level"),
        default=0.1,
        help_text=_("AI response creativity level (0.0 = very focused, 2.0 = very creative). Recommended: 0.1-0.3 for business use.")
    )

    def __str__(self):
        return self.name

    def branches_count(self):
        return Branch.objects.filter(branch__company=self).count()

    def clean(self):
        """Validate AI configuration fields"""
        super().clean()

        # Validate AI temperature range
        if self.ai_temperature is not None:
            if not (0.0 <= self.ai_temperature <= 2.0):
                raise ValidationError({
                    'ai_temperature': _('AI temperature must be between 0.0 and 2.0')
                })

        # Validate enabled_tools_json is a list
        if self.enabled_tools_json is not None:
            if not isinstance(self.enabled_tools_json, list):
                raise ValidationError({
                    'enabled_tools_json': _('Enabled tools must be a list of tool names')
                })

        # Validate database_config_json is a dict
        if self.database_config_json is not None:
            if not isinstance(self.database_config_json, dict):
                raise ValidationError({
                    'database_config_json': _('Database configuration must be a dictionary')
                })

    def get_ai_instructions(self):
        """Get AI instructions for this company (custom or default)"""
        if self.ai_instructions_template:
            return self.ai_instructions_template

        # Return default instructions based on company activity
        return f"""
🏢 **{self.name} Business Intelligence Assistant**

You are the dedicated AI assistant for {self.name}, specializing in {self.activity_name}.

**🎯 YOUR MISSION:**
1. **BUSINESS ANALYTICS**: Provide insights specific to {self.activity_name}
2. **DATA ANALYSIS**: Help analyze business data and trends
3. **DECISION SUPPORT**: Support data-driven business decisions
4. **OPERATIONAL EFFICIENCY**: Optimize business processes and operations

**🔒 SECURITY SCOPE:**
- Access ONLY {self.name}'s authorized database
- Maintain strict data confidentiality and security
- Provide business-focused insights and recommendations
- Support {self.name}'s specific business objectives

Remember: You exist solely to serve {self.name}'s business intelligence needs.
"""

    def get_enabled_tools(self):
        """Get list of enabled AI tools for this company"""
        if self.enabled_tools_json:
            return self.enabled_tools_json

        # Use the AI Tools Registry to get default tools based on subscription
        from product.ai_tools_registry import AIToolsRegistry
        return AIToolsRegistry.get_tools_for_company(self)

    def get_company_assistant_id(self):
        """Get company-specific AI assistant ID if it exists"""
        # Use the discovery system to find company-specific assistant
        company_slug = self.name.lower().replace(' ', '_').replace('-', '_')
        expected_assistant_id = f"{company_slug}_ai_assistant"

        try:
            # Import the discovery system
            from product.assistants import COMPANY_ASSISTANTS

            # Check if assistant exists in registry
            if expected_assistant_id in COMPANY_ASSISTANTS:
                return expected_assistant_id

            return None
        except ImportError:
            # Fallback if discovery system not available
            return None

    def has_dedicated_assistant(self):
        """Check if company has a dedicated AI assistant"""
        return self.get_company_assistant_id() is not None

    # ==================== WEBSITE WIDGET CONFIGURATION ====================
    # Add widget configuration fields directly to Company model

    widget_welcome_message = models.TextField(
        _("Widget Welcome Message"),
        blank=True,
        help_text=_("Welcome message shown to website visitors. Leave blank for default.")
    )

    widget_theme_config = models.JSONField(
        _("Widget Theme Configuration"),
        default=dict,
        blank=True,
        help_text=_("Widget appearance settings (colors, fonts, etc.)")
    )

    widget_position = models.CharField(
        _("Widget Position"),
        max_length=20,
        choices=[
            ('bottom-right', _('Bottom Right')),
            ('bottom-left', _('Bottom Left')),
            ('top-right', _('Top Right')),
            ('top-left', _('Top Left')),
        ],
        default='bottom-right',
        help_text=_("Widget position on the website")
    )

    widget_is_active = models.BooleanField(
        _("Widget Active"),
        default=True,
        help_text=_("Whether the website widget is active")
    )

    def get_widget_welcome_message(self):
        """Get widget welcome message with fallback"""
        if self.widget_welcome_message:
            return self.widget_welcome_message
        return f"Hello! How can {self.name} help you today?"

    def get_widget_theme_config(self):
        """Get widget theme configuration with defaults"""
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
        if self.widget_theme_config:
            theme.update(self.widget_theme_config)
        return theme


class Branch(models.Model):
    STATUS_CHOICES = {
        ENABLED: _("Enabled"),
        DISABLED: _("Disabled"),
    }
    company = models.ForeignKey(Company, related_name='branches', on_delete=models.CASCADE)
    name = models.CharField(_("Name"), max_length=200)
    address = models.TextField(_("Address"))
    status = models.CharField(_("Branch Status"), max_length=1, choices=STATUS_CHOICES)

    def __str__(self):
        return self.name
