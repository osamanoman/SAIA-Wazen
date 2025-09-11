from django.contrib import admin
from django.utils.html import format_html

from product.models import (
    Product, KnowledgeCategory, KnowledgeArticle, KnowledgeSearchLog,
    FAQ, FAQAlias, ServiceOrder, ServiceOrderCache
)
from saia.mixins import CompanyFilterMixin


# Register your models here.

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin, CompanyFilterMixin):
    list_display = ('id', 'name', 'price', 'type', 'is_service_orderable', 'quantity', 'expiration', 'company', 'created_at')
    search_fields = ('name', 'price', 'type', 'service_description')
    list_filter = ('price', 'type', 'is_service_orderable', 'requires_customer_info', 'expiration', 'company')
    list_editable = ('is_service_orderable',)

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'price', 'type', 'quantity', 'expiration', 'company')
        }),
        ('Service Configuration', {
            'fields': ('is_service_orderable', 'service_description', 'requires_customer_info'),
            'description': 'Configure service ordering through AI assistant',
            'classes': ('collapse',)
        })
    )

    def get_queryset(self, request):
        """Filter products by company for customer users"""
        return self.filter_by_company(request, super().get_queryset(request))

    def save_model(self, request, obj, form, change):
        """Auto-assign company for customer users when creating products"""
        if not change and hasattr(request.user, 'is_customer') and request.user.is_customer:
            if request.user.company:
                obj.company = request.user.company
        super().save_model(request, obj, form, change)


# ==================== KNOWLEDGE BASE ADMIN ====================

@admin.register(KnowledgeCategory)
class KnowledgeCategoryAdmin(admin.ModelAdmin, CompanyFilterMixin):
    list_display = ('name', 'company', 'article_count', 'display_order', 'is_active', 'created_at')
    list_filter = ('company', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'company__name')
    ordering = ('company', 'display_order', 'name')
    list_editable = ('display_order', 'is_active')

    def article_count(self, obj):
        count = obj.articles.filter(is_active=True).count()
        return format_html(
            '<span style="color: {};">{}</span>',
            '#28a745' if count > 0 else '#6c757d',
            count
        )
    article_count.short_description = 'Active Articles'

    def get_queryset(self, request):
        """Filter categories by company for customer users"""
        qs = super().get_queryset(request)
        return self.filter_by_company(request, qs)

    def save_model(self, request, obj, form, change):
        """Auto-assign company for customer users"""
        if not change and hasattr(request.user, 'is_customer') and request.user.is_customer:
            if request.user.company:
                obj.company = request.user.company
        super().save_model(request, obj, form, change)


@admin.register(KnowledgeArticle)
class KnowledgeArticleAdmin(admin.ModelAdmin, CompanyFilterMixin):
    list_display = ('title', 'company', 'category', 'article_type', 'locale', 'published', 'display_order', 'is_outdated_display', 'updated_at')
    list_filter = ('company', 'category', 'article_type', 'locale', 'published', 'is_active', 'created_at')
    search_fields = ('title', 'content', 'content_md', 'keywords', 'company__name', 'category__name')
    ordering = ('company', 'category', 'display_order', 'title')
    list_editable = ('display_order', 'published')
    list_per_page = 25  # Show 25 items per page
    list_max_show_all = 100  # Show "Show all" link if less than 100 items
    readonly_fields = ('slug', 'last_reviewed_at')

    fieldsets = (
        ('Basic Information', {
            'fields': ('company', 'category', 'title', 'slug', 'article_type', 'locale')
        }),
        ('Content', {
            'fields': ('content_md', 'content', 'keywords', 'tags'),
            'description': 'Use Markdown format for better formatting. Legacy content field will be phased out.'
        }),
        ('Publishing', {
            'fields': ('published', 'is_active', 'display_order', 'last_reviewed_at'),
            'classes': ('collapse',)
        })
    )

    def is_outdated_display(self, obj):
        """Display if content needs review"""
        if obj.is_outdated:
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">⚠️ Needs Review</span>'
            )
        return format_html(
            '<span style="color: #28a745;">✅ Current</span>'
        )
    is_outdated_display.short_description = 'Content Status'

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related('company', 'category')
        return self.filter_by_company(request, qs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filter category choices by user's company"""
        if db_field.name == "category":
            if hasattr(request.user, 'is_customer') and request.user.is_customer and request.user.company:
                kwargs["queryset"] = KnowledgeCategory.objects.filter(company=request.user.company)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        """Auto-assign company for customer users"""
        if not change and hasattr(request.user, 'is_customer') and request.user.is_customer:
            if request.user.company:
                obj.company = request.user.company
        super().save_model(request, obj, form, change)


# ==================== FAQ ADMIN ====================

class FAQAliasInline(admin.TabularInline):
    model = FAQAlias
    extra = 1
    fields = ('phrasing',)


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin, CompanyFilterMixin):
    list_display = ('question_short', 'company', 'locale', 'published', 'display_order', 'is_outdated_display', 'updated_at')
    list_filter = ('company', 'locale', 'published', 'is_active', 'created_at')
    search_fields = ('question', 'answer_md', 'tags', 'company__name')
    ordering = ('company', 'display_order', 'question')
    list_editable = ('display_order', 'published')
    list_per_page = 25
    readonly_fields = ('last_reviewed_at',)
    inlines = [FAQAliasInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('company', 'question', 'locale')
        }),
        ('Answer', {
            'fields': ('answer_md', 'tags'),
            'description': 'Use Markdown format for better formatting'
        }),
        ('Publishing', {
            'fields': ('published', 'is_active', 'display_order', 'last_reviewed_at'),
            'classes': ('collapse',)
        })
    )

    def question_short(self, obj):
        """Display shortened question"""
        return obj.question[:60] + '...' if len(obj.question) > 60 else obj.question
    question_short.short_description = 'Question'

    def is_outdated_display(self, obj):
        """Display if FAQ needs review"""
        if obj.is_outdated:
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">⚠️ Needs Review</span>'
            )
        return format_html(
            '<span style="color: #28a745;">✅ Current</span>'
        )
    is_outdated_display.short_description = 'Content Status'

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related('company')
        return self.filter_by_company(request, qs)

    def save_model(self, request, obj, form, change):
        """Auto-assign company for customer users"""
        if not change and hasattr(request.user, 'is_customer') and request.user.is_customer:
            if request.user.company:
                obj.company = request.user.company
        super().save_model(request, obj, form, change)


@admin.register(KnowledgeSearchLog)
class KnowledgeSearchLogAdmin(admin.ModelAdmin, CompanyFilterMixin):
    list_display = ('query', 'company', 'results_count', 'created_at')
    list_filter = ('company', 'results_count', 'created_at')
    search_fields = ('query', 'company__name')
    ordering = ('-created_at',)
    readonly_fields = ('query', 'company', 'results_count', 'user_agent', 'ip_address', 'created_at')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return self.filter_by_company(request, qs)

    def has_add_permission(self, request):
        return False  # Search logs are created automatically

    def has_change_permission(self, request, obj=None):
        return False  # Search logs should not be modified


# ==================== SERVICE ORDER ADMIN ====================

@admin.register(ServiceOrder)
class ServiceOrderAdmin(admin.ModelAdmin, CompanyFilterMixin):
    list_display = ('order_number', 'customer_name', 'customer_phone', 'service', 'status', 'company', 'created_by', 'created_at')
    list_filter = ('status', 'company', 'service', 'created_at')
    search_fields = ('customer_name', 'customer_id', 'customer_phone', 'order_notes', 'company__name')
    ordering = ('-created_at',)
    list_editable = ('status',)
    readonly_fields = ('id', 'order_number', 'created_at', 'updated_at', 'confirmed_at')

    fieldsets = (
        ('Order Information', {
            'fields': ('id', 'order_number', 'company', 'created_by', 'service', 'status')
        }),
        ('Customer Information', {
            'fields': ('customer_name', 'customer_age', 'customer_id', 'customer_phone', 'customer_image'),
            'description': 'Customer information collected by the AI assistant'
        }),
        ('Order Details', {
            'fields': ('order_notes', 'ai_session_data'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'confirmed_at'),
            'classes': ('collapse',)
        })
    )

    def get_queryset(self, request):
        """Filter service orders by company for customer users"""
        qs = super().get_queryset(request).select_related('company', 'created_by', 'service')
        return self.filter_by_company(request, qs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filter service choices by user's company and orderable services"""
        if db_field.name == "service":
            if hasattr(request.user, 'is_customer') and request.user.is_customer and request.user.company:
                kwargs["queryset"] = Product.objects.filter(
                    company=request.user.company,
                    type='service',
                    is_service_orderable=True
                )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        """Auto-assign company and created_by for customer users"""
        if not change:
            if hasattr(request.user, 'is_customer') and request.user.is_customer:
                if request.user.company:
                    obj.company = request.user.company
                obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ServiceOrderCache)
class ServiceOrderCacheAdmin(admin.ModelAdmin, CompanyFilterMixin):
    list_display = ('session_key', 'user', 'company', 'service', 'is_complete', 'is_expired', 'created_at', 'expires_at')
    list_filter = ('company', 'service', 'created_at', 'expires_at')
    search_fields = ('session_key', 'user__username', 'company__name')
    ordering = ('-created_at',)
    readonly_fields = ('session_key', 'user', 'company', 'is_complete', 'is_expired', 'created_at', 'updated_at')

    fieldsets = (
        ('Cache Information', {
            'fields': ('session_key', 'user', 'company', 'service')
        }),
        ('Cached Data', {
            'fields': ('cached_data', 'is_complete'),
            'description': 'Temporarily stored customer information'
        }),
        ('Expiration', {
            'fields': ('created_at', 'updated_at', 'expires_at', 'is_expired'),
            'classes': ('collapse',)
        })
    )

    def get_queryset(self, request):
        """Filter cache entries by company for customer users"""
        qs = super().get_queryset(request).select_related('user', 'company', 'service')
        return self.filter_by_company(request, qs)

    def has_add_permission(self, request):
        return False  # Cache entries are created automatically by AI assistant

    def has_change_permission(self, request, obj=None):
        return False  # Cache entries should not be modified manually
