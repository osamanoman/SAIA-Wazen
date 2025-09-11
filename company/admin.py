from django.contrib import admin
from django.utils.html import format_html
from django import forms
from django.utils.safestring import mark_safe
from django.contrib import messages

from .models import Company, Branch
from product.ai_tools_registry import AIToolsRegistry, ToolCategory
from .signals import generate_assistant_for_existing_company


# Register your models here.

class InlineBranch(admin.StackedInline):
    model = Branch
    extra = 1


class CompanyAdminForm(forms.ModelForm):
    """Custom form for Company admin with enhanced AI configuration fields"""

    # Add dynamic fields for AI tools
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add AI tools checkboxes dynamically
        self._add_ai_tools_fields()

        # Set initial values for AI tools if instance exists
        if self.instance and self.instance.pk:
            self._set_initial_tool_values()

    def _add_ai_tools_fields(self):
        """Add checkbox fields for each AI tool"""
        try:
            tools_by_category = {}

            # Group tools by category
            for tool_name, tool_info in AIToolsRegistry.get_all_tools().items():
                category = tool_info.category.value
                if category not in tools_by_category:
                    tools_by_category[category] = []
                tools_by_category[category].append((tool_name, tool_info))

            # Create fields for each tool
            for category, tools in tools_by_category.items():
                for tool_name, tool_info in tools:
                    field_name = f'ai_tool_{tool_name}'
                    self.fields[field_name] = forms.BooleanField(
                        label=tool_info.display_name,
                        help_text=f"{tool_info.description} (Category: {category.title()}, Level: {tool_info.subscription_level.value.title()})",
                        required=False,
                        initial=True  # Default to enabled
                    )
        except Exception as e:
            # If there's any issue with AI tools registry, just skip adding dynamic fields
            # This prevents the admin from breaking if there are registry issues
            pass

    def _set_initial_tool_values(self):
        """Set initial values for tool checkboxes based on company configuration"""
        try:
            if hasattr(self.instance, 'enabled_tools_json') and self.instance.enabled_tools_json:
                enabled_tools = self.instance.enabled_tools_json
            else:
                # Use default tools from registry
                enabled_tools = AIToolsRegistry.get_tools_for_company(self.instance)

            # Set checkbox values
            for tool_name in AIToolsRegistry.get_all_tools().keys():
                field_name = f'ai_tool_{tool_name}'
                if field_name in self.fields:
                    self.fields[field_name].initial = tool_name in enabled_tools
        except Exception as e:
            # If there's any issue, just skip setting initial values
            pass

    def save(self, commit=True):
        """Save the form and update enabled_tools_json based on checkboxes"""
        instance = super().save(commit=False)

        try:
            # Collect enabled tools from checkboxes
            enabled_tools = []
            for field_name, field in self.fields.items():
                if field_name.startswith('ai_tool_') and self.cleaned_data.get(field_name):
                    tool_name = field_name.replace('ai_tool_', '')
                    enabled_tools.append(tool_name)

            # Update enabled_tools_json
            instance.enabled_tools_json = enabled_tools
        except Exception as e:
            # If there's any issue with AI tools, just skip updating them
            pass

        if commit:
            instance.save()
        return instance

    class Meta:
        model = Company
        fields = '__all__'
        widgets = {
            'ai_instructions_template': forms.Textarea(attrs={
                'rows': 10,
                'cols': 80,
                'placeholder': 'Enter custom AI instructions for this company...'
            }),
            'database_config_json': forms.Textarea(attrs={
                'rows': 5,
                'cols': 80,
                'placeholder': '{"host": "db.company.com", "name": "company_db", "user": "readonly_user"}'
            }),
        }


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    # Temporarily disable the custom form to fix the field validation issue
    # form = CompanyAdminForm
    inlines = [InlineBranch, ]
    list_display = ('id', 'name', 'activity_name', 'activity_type', 'number_of_branches', 'active', 'ai_configured', 'has_dedicated_assistant')
    list_filter = ('activity_type', 'activity_status', 'subscription_status', 'ai_language')
    search_fields = ('name', 'activity_name', 'email')
    actions = ['generate_ai_assistant']

    fieldsets = [
        ('Company Information', {
            'fields': ('name', 'email', 'phone', 'activity_name', 'activity_type', 'activity_status')
        }),
        ('Subscription Details', {
            'fields': ('subscription_start_date', 'subscription_end_date', 'subscription_status')
        }),
        ('AI Assistant Configuration', {
            'fields': ('ai_language', 'ai_temperature', 'ai_instructions_template', 'enabled_tools_json', 'database_config_json'),
            'description': 'Configure the AI assistant behavior for this company. All fields are optional - leave blank to use system defaults.',
            'classes': ('collapse',),
        }),
    ]

    def active(self, obj):
        if obj.activity_status == "1":
            return format_html('<img src="/static/admin/img/icon-yes.svg" alt="True">')
        return format_html('<img src="/static/admin/img/icon-no.svg" alt="True">')
    active.short_description = 'Active'

    def number_of_branches(self, obj):
        return obj.branches.count() if obj else 0
    number_of_branches.short_description = 'Branches'

    def ai_configured(self, obj):
        """Show if company has AI configuration"""
        has_config = bool(
            obj.ai_instructions_template or
            obj.enabled_tools_json or
            obj.database_config_json or
            obj.ai_language != 'en' or
            obj.ai_temperature != 0.1
        )
        if has_config:
            return format_html('<img src="/static/admin/img/icon-yes.svg" alt="Configured"> Custom')
        return format_html('<img src="/static/admin/img/icon-no.svg" alt="Default"> Default')
    ai_configured.short_description = 'AI Config'

    def has_dedicated_assistant(self, obj):
        """Show if company has a dedicated AI assistant"""
        if obj.has_dedicated_assistant():
            return format_html('<img src="/static/admin/img/icon-yes.svg" alt="Yes"> Dedicated')
        return format_html('<img src="/static/admin/img/icon-no.svg" alt="No"> Shared')
    has_dedicated_assistant.short_description = 'AI Assistant'

    def generate_ai_assistant(self, request, queryset):
        """Admin action to generate AI assistants for selected companies"""
        success_count = 0
        error_count = 0

        for company in queryset:
            if generate_assistant_for_existing_company(company.id):
                success_count += 1
            else:
                error_count += 1

        if success_count > 0:
            messages.success(request, f"Successfully generated AI assistants for {success_count} companies.")
        if error_count > 0:
            messages.error(request, f"Failed to generate AI assistants for {error_count} companies.")

    generate_ai_assistant.short_description = "Generate dedicated AI assistants for selected companies"

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'address', 'active')
    # readonly_fields = ['active']

    def active(self, obj):
        if obj.status == "1":
            return format_html('<img src="/static/admin/img/icon-yes.svg" alt="True">')
        return format_html('<img src="/static/admin/img/icon-no.svg" alt="True">')
