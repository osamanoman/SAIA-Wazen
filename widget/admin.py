from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import WebsiteSession, SessionHandover


@admin.register(WebsiteSession)
class WebsiteSessionAdmin(admin.ModelAdmin):
    list_display = [
        'session_id_short', 'company', 'status', 'message_count',
        'duration_display', 'visitor_ip', 'created_at'
    ]
    list_filter = ['status', 'company', 'created_at']
    search_fields = ['session_id', 'visitor_ip', 'user_agent']
    readonly_fields = [
        'session_id', 'thread', 'created_at', 'last_activity',
        'closed_at', 'duration_display', 'message_count'
    ]

    fieldsets = (
        ('Session Info', {
            'fields': ('session_id', 'thread', 'company', 'status')
        }),
        ('Timing', {
            'fields': ('created_at', 'last_activity', 'closed_at', 'duration_display')
        }),
        ('Visitor Info', {
            'fields': ('visitor_ip', 'user_agent', 'referrer_url')
        }),
        ('Metadata', {
            'fields': ('visitor_metadata', 'message_count'),
            'classes': ('collapse',)
        }),
    )

    def session_id_short(self, obj):
        """Display shortened session ID"""
        return str(obj.session_id)[:8] + '...'
    session_id_short.short_description = 'Session ID'

    def duration_display(self, obj):
        """Display formatted duration"""
        if obj.duration_minutes < 1:
            return "< 1 min"
        elif obj.duration_minutes < 60:
            return f"{obj.duration_minutes} min"
        else:
            hours = obj.duration_minutes // 60
            minutes = obj.duration_minutes % 60
            return f"{hours}h {minutes}m"
    duration_display.short_description = 'Duration'

    def message_count(self, obj):
        """Display message count with link to thread"""
        count = obj.get_message_count()
        if count > 0:
            # Link to thread in admin (if thread admin exists)
            return format_html(
                '<a href="/admin/django_ai_assistant/thread/{}/change/">{} messages</a>',
                obj.thread.id, count
            )
        return "0 messages"
    message_count.short_description = 'Messages'

    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related('company', 'thread')


@admin.register(SessionHandover)
class SessionHandoverAdmin(admin.ModelAdmin):
    list_display = [
        'session_short', 'status', 'priority', 'assigned_agent',
        'response_time_display', 'requested_at'
    ]
    list_filter = ['status', 'priority', 'assigned_agent', 'requested_at']
    search_fields = ['session__session_id', 'reason', 'notes']
    readonly_fields = [
        'requested_at', 'assigned_at', 'completed_at',
        'response_time_display', 'resolution_time_display'
    ]

    fieldsets = (
        ('Handover Info', {
            'fields': ('session', 'status', 'priority', 'reason')
        }),
        ('Assignment', {
            'fields': ('assigned_agent', 'notes')
        }),
        ('Timing', {
            'fields': (
                'requested_at', 'assigned_at', 'completed_at',
                'response_time_display', 'resolution_time_display'
            )
        }),
        ('Feedback', {
            'fields': ('customer_rating', 'customer_feedback'),
            'classes': ('collapse',)
        }),
    )

    def session_short(self, obj):
        """Display shortened session ID"""
        return str(obj.session.session_id)[:8] + '...'
    session_short.short_description = 'Session'

    def response_time_display(self, obj):
        """Display response time"""
        time = obj.response_time_minutes
        if time is None:
            return "Pending"
        elif time < 60:
            return f"{time} min"
        else:
            hours = time // 60
            minutes = time % 60
            return f"{hours}h {minutes}m"
    response_time_display.short_description = 'Response Time'

    def resolution_time_display(self, obj):
        """Display resolution time"""
        time = obj.resolution_time_minutes
        if time is None:
            return "Not completed"
        elif time < 60:
            return f"{time} min"
        else:
            hours = time // 60
            minutes = time % 60
            return f"{hours}h {minutes}m"
    resolution_time_display.short_description = 'Resolution Time'

    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related(
            'session', 'session__company', 'assigned_agent'
        )
