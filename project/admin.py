from django.contrib import admin
from django.contrib.admin.options import InlineModelAdmin
from django.urls import reverse
from django.utils.safestring import mark_safe
from typing import ClassVar, List, Type

from django_ai_assistant.models import Message, Thread
from saia.mixins import CompanyFilterMixin


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    fields = ("pk", "message_type", "content", "created_at")
    readonly_fields = fields
    ordering = ("created_at",)
    show_change_link = True

    def pk(self, obj):
        display_text = "<a href={}>{}</a>".format(
            reverse(
                f"admin:{Message._meta.app_label}_{Message._meta.model_name}_change", args=(obj.pk,)
            ),
            obj.pk,
        )
        return mark_safe(display_text)  # noqa: S308

    def message_type(self, obj):
        return obj.message.get("type") if obj.message else None

    def content(self, obj):
        content = obj.message.get("data", {}).get("content") if obj.message else None
        if content and len(content) > 100:
            return content[:100] + "..."
        return content

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


# Unregister the default admin classes
admin.site.unregister(Thread)
admin.site.unregister(Message)


@admin.register(Thread)
class CustomThreadAdmin(admin.ModelAdmin, CompanyFilterMixin):
    list_display = ("name", "created_at", "created_by", "updated_at", "assistant_id")
    search_fields = ("name", "created_by__username")
    list_filter = ("created_at", "updated_at", "assistant_id")
    raw_id_fields = ("created_by",)
    inlines: ClassVar[List[Type[InlineModelAdmin]]] = [MessageInline]

    def get_queryset(self, request):
        """Filter threads for customer users"""
        qs = super().get_queryset(request)

        # SAIA admins see all threads
        if hasattr(request.user, 'is_saia_admin') and request.user.is_saia_admin():
            return qs

        # Customer users see only their own threads
        if hasattr(request.user, 'is_customer') and request.user.is_customer:
            return qs.filter(created_by=request.user)

        # Default: no access
        return qs.none()


@admin.register(Message)
class CustomMessageAdmin(admin.ModelAdmin, CompanyFilterMixin):
    list_display = ("id", "thread", "message_type", "content_preview", "created_at")
    search_fields = ("thread__name", "message")
    list_filter = ("created_at",)
    raw_id_fields = ("thread",)

    def message_type(self, obj):
        return obj.message.get("type") if obj.message else None
    message_type.short_description = "Type"

    def content_preview(self, obj):
        content = obj.message.get("data", {}).get("content") if obj.message else None
        if content and len(content) > 50:
            return content[:50] + "..."
        return content
    content_preview.short_description = "Content"

    def get_queryset(self, request):
        """Filter messages for customer users"""
        qs = super().get_queryset(request)

        # SAIA admins see all messages
        if hasattr(request.user, 'is_saia_admin') and request.user.is_saia_admin():
            return qs

        # Customer users see only messages from their own threads
        if hasattr(request.user, 'is_customer') and request.user.is_customer:
            return qs.filter(thread__created_by=request.user)

        # Default: no access
        return qs.none()
