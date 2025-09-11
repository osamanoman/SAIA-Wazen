from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from datetime import date
import uuid

User = get_user_model()


# Create your models here.

class Product(models.Model):
    PRODUCT_TYPE_CHOICES = [
        ('product', _('Product')),
        ('service', _('Service')),
        ('none', _('None')),
    ]

    name = models.CharField(_("Product Name"), max_length=100)
    price = models.FloatField(_("Price"))
    type = models.CharField(_("Product Type"), max_length=100, choices=PRODUCT_TYPE_CHOICES, default='none')
    quantity = models.FloatField(_("Quantity"), default=0)
    expiration = models.DateField(_("Expire Date"), default=date.today)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # NEW: Add company relationship for data isolation
    company = models.ForeignKey(
        'company.Company',
        on_delete=models.CASCADE,
        null=True,  # Allow null for existing data
        blank=True,
        help_text=_("Company that owns this product")
    )

    # NEW: Service-specific fields
    is_service_orderable = models.BooleanField(
        _("Service Orderable"),
        default=False,
        help_text=_("Whether this service can be ordered through the AI assistant")
    )

    service_description = models.TextField(
        _("Service Description"),
        blank=True,
        null=True,
        help_text=_("Detailed description of the service for AI assistant")
    )

    requires_customer_info = models.BooleanField(
        _("Requires Customer Info"),
        default=True,
        help_text=_("Whether this service requires customer information collection")
    )

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ("created_at",)

    def __str__(self):
        return self.name


# ==================== KNOWLEDGE BASE MODELS FOR TEXT-BASED CUSTOMER SUPPORT ====================

class KnowledgeCategory(models.Model):
    """Categories for organizing knowledge content (e.g., Services, Policies, FAQ)"""

    company = models.ForeignKey(
        'company.Company',
        on_delete=models.CASCADE,
        related_name='knowledge_categories',
        help_text=_("Company this category belongs to")
    )
    name = models.CharField(_("Category Name"), max_length=100)
    description = models.TextField(_("Description"), blank=True)
    display_order = models.PositiveIntegerField(_("Display Order"), default=0)
    is_active = models.BooleanField(_("Active"), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Knowledge Category")
        verbose_name_plural = _("Knowledge Categories")
        ordering = ['company', 'display_order', 'name']
        unique_together = ['company', 'name']

    def __str__(self):
        return f"{self.company.name} - {self.name}"


class KnowledgeArticle(models.Model):
    """Individual knowledge articles with full-text search capabilities"""

    ARTICLE_TYPES = [
        ('service', _('Service Description')),
        ('policy', _('Policy/Terms')),
        ('faq', _('FAQ')),
        ('procedure', _('Procedure')),
        ('general', _('General Information')),
    ]

    company = models.ForeignKey(
        'company.Company',
        on_delete=models.CASCADE,
        related_name='knowledge_articles',
        help_text=_("Company this article belongs to")
    )
    category = models.ForeignKey(
        KnowledgeCategory,
        on_delete=models.CASCADE,
        related_name='articles'
    )
    title = models.CharField(_("Title"), max_length=200)
    slug = models.SlugField(
        _("Slug"),
        max_length=250,
        blank=True,
        null=True,
        help_text=_("URL-friendly identifier (auto-generated from title)")
    )
    content = models.TextField(_("Content (Legacy)"), help_text=_("Plain text content - being migrated to Markdown"))
    content_md = models.TextField(
        _("Content (Markdown)"),
        blank=True,
        help_text=_("Content in Markdown format for better formatting")
    )
    article_type = models.CharField(_("Article Type"), max_length=20, choices=ARTICLE_TYPES, default='general')
    keywords = models.TextField(
        _("Keywords"),
        blank=True,
        help_text=_("Comma-separated keywords for better search results")
    )
    tags = models.JSONField(
        _("Tags"),
        default=list,
        blank=True,
        help_text=_("Structured tags for better categorization")
    )
    locale = models.CharField(
        _("Language"),
        max_length=5,
        default='ar',
        choices=[('ar', 'Arabic'), ('en', 'English')],
        help_text=_("Content language")
    )
    is_active = models.BooleanField(_("Active"), default=True)
    published = models.BooleanField(_("Published"), default=True)
    display_order = models.PositiveIntegerField(_("Display Order"), default=0)
    last_reviewed_at = models.DateTimeField(
        _("Last Reviewed"),
        auto_now=True,
        help_text=_("When this content was last reviewed for accuracy")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Knowledge Article")
        verbose_name_plural = _("Knowledge Articles")
        ordering = ['company', 'category', 'display_order', 'title']
        unique_together = [
            ['company', 'title'],  # Prevent duplicate titles within same company
            ['company', 'slug'],   # Prevent duplicate slugs within same company
        ]
        indexes = [
            models.Index(fields=['company', 'is_active']),
            models.Index(fields=['company', 'article_type']),
            models.Index(fields=['company', 'locale', 'published']),
            models.Index(fields=['company', 'last_reviewed_at']),
            # Full-text search indexes
            models.Index(fields=['title']),
            models.Index(fields=['content']),
        ]

    def save(self, *args, **kwargs):
        """Auto-generate slug from title if not provided"""
        if not self.slug:
            from django.utils.text import slugify
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1

            # Ensure unique slug within company
            while KnowledgeArticle.objects.filter(
                company=self.company,
                slug=slug
            ).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.company.name} - {self.title}"

    def get_keywords_list(self):
        """Return keywords as a list"""
        if self.keywords:
            return [k.strip() for k in self.keywords.split(',') if k.strip()]
        return []

    def get_content(self):
        """Return Markdown content if available, otherwise plain content"""
        return self.content_md if self.content_md else self.content

    def get_tags_list(self):
        """Return tags as a list"""
        return self.tags if isinstance(self.tags, list) else []

    @property
    def is_outdated(self):
        """Check if content needs review (older than 6 months)"""
        from datetime import datetime, timedelta
        from django.utils import timezone

        if not self.last_reviewed_at:
            return True

        six_months_ago = timezone.now() - timedelta(days=180)
        return self.last_reviewed_at < six_months_ago


class FAQ(models.Model):
    """Dedicated FAQ model for better question-answer management"""

    company = models.ForeignKey(
        'company.Company',
        on_delete=models.CASCADE,
        related_name='faqs',
        help_text=_("Company this FAQ belongs to")
    )
    question = models.TextField(_("Question"))
    answer_md = models.TextField(
        _("Answer (Markdown)"),
        help_text=_("Answer in Markdown format for better formatting")
    )
    tags = models.JSONField(
        _("Tags"),
        default=list,
        blank=True,
        help_text=_("Tags for categorization and search")
    )
    locale = models.CharField(
        _("Language"),
        max_length=5,
        default='ar',
        choices=[('ar', 'Arabic'), ('en', 'English')]
    )
    is_active = models.BooleanField(_("Active"), default=True)
    published = models.BooleanField(_("Published"), default=True)
    display_order = models.PositiveIntegerField(_("Display Order"), default=0)
    last_reviewed_at = models.DateTimeField(
        _("Last Reviewed"),
        auto_now=True,
        help_text=_("When this FAQ was last reviewed for accuracy")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("FAQ")
        verbose_name_plural = _("FAQs")
        ordering = ['company', 'display_order', 'question']
        unique_together = [['company', 'question']]
        indexes = [
            models.Index(fields=['company', 'is_active', 'published']),
            models.Index(fields=['company', 'locale']),
            models.Index(fields=['question']),
        ]

    def __str__(self):
        return f"{self.company.name} - {self.question[:50]}{'...' if len(self.question) > 50 else ''}"

    def get_tags_list(self):
        """Return tags as a list"""
        return self.tags if isinstance(self.tags, list) else []

    @property
    def is_outdated(self):
        """Check if FAQ needs review (older than 6 months)"""
        from datetime import timedelta
        from django.utils import timezone

        if not self.last_reviewed_at:
            return True

        six_months_ago = timezone.now() - timedelta(days=180)
        return self.last_reviewed_at < six_months_ago


class FAQAlias(models.Model):
    """Alternative phrasings for FAQ questions to improve matching"""

    faq = models.ForeignKey(
        FAQ,
        on_delete=models.CASCADE,
        related_name='aliases'
    )
    phrasing = models.TextField(
        _("Alternative Phrasing"),
        help_text=_("Alternative way to ask the same question")
    )

    class Meta:
        verbose_name = _("FAQ Alias")
        verbose_name_plural = _("FAQ Aliases")
        unique_together = [['faq', 'phrasing']]

    def __str__(self):
        return f"{self.faq.question[:30]}... → {self.phrasing[:30]}..."


class KnowledgeSearchLog(models.Model):
    """Log search queries for analytics and improvement"""

    company = models.ForeignKey('company.Company', on_delete=models.CASCADE, related_name='search_logs')
    query = models.CharField(_("Search Query"), max_length=500)
    results_count = models.PositiveIntegerField(_("Results Count"))
    user_agent = models.TextField(_("User Agent"), blank=True)
    ip_address = models.GenericIPAddressField(_("IP Address"), blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Knowledge Search Log")
        verbose_name_plural = _("Knowledge Search Logs")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.company.name} - {self.query[:50]}{'...' if len(self.query) > 50 else ''}"


# ==================== SERVICE ORDERING MODELS ====================

class ServiceOrderStatus(models.TextChoices):
    """Status choices for service orders"""
    DRAFT = 'draft', _('Draft')
    UNDER_REVIEW = 'under_review', _('Under Review')
    APPROVED = 'approved', _('Approved')
    IN_PROGRESS = 'in_progress', _('In Progress')
    COMPLETED = 'completed', _('Completed')
    CANCELLED = 'cancelled', _('Cancelled')


class ServiceOrder(models.Model):
    """
    Service Order Model

    Stores service orders created through the AI assistant.
    Includes customer information and order status tracking.
    """

    # Primary identification
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text=_("Unique identifier for the service order")
    )

    # Company and user relationships
    company = models.ForeignKey(
        'company.Company',
        on_delete=models.CASCADE,
        help_text=_("Company this order belongs to")
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='service_orders',
        help_text=_("User who created this order")
    )

    # Service relationship
    service = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        limit_choices_to={'type': 'service', 'is_service_orderable': True},
        help_text=_("Service being ordered")
    )

    # Customer information (collected by AI)
    customer_name = models.CharField(
        _("Customer Name"),
        max_length=255,
        help_text=_("Full name of the customer")
    )

    customer_age = models.PositiveIntegerField(
        _("Customer Age"),
        help_text=_("Age of the customer")
    )

    customer_id = models.CharField(
        _("Customer ID"),
        max_length=10,
        help_text=_("Customer identification number (10 digits)")
    )

    customer_phone = models.CharField(
        _("Customer Phone"),
        max_length=10,
        help_text=_("Customer phone number (9 digits starting with 5, or 10 digits starting with 05)")
    )

    customer_image = models.ImageField(
        _("Customer Image"),
        upload_to='service_orders/customer_images/',
        blank=True,
        null=True,
        help_text=_("Customer personal image (required)")
    )

    # Order details
    order_notes = models.TextField(
        _("Order Notes"),
        blank=True,
        null=True,
        help_text=_("Additional notes or requirements for the order")
    )

    # Status and tracking
    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=ServiceOrderStatus.choices,
        default=ServiceOrderStatus.UNDER_REVIEW,
        help_text=_("Current status of the service order")
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("When the order was created")
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text=_("When the order was last updated")
    )

    confirmed_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text=_("When the customer confirmed the order data")
    )

    # AI assistant metadata
    ai_session_data = models.JSONField(
        _("AI Session Data"),
        default=dict,
        blank=True,
        help_text=_("Metadata from the AI assistant session")
    )

    class Meta:
        verbose_name = _("Service Order")
        verbose_name_plural = _("Service Orders")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['company', 'status']),
            models.Index(fields=['created_by', 'status']),
            models.Index(fields=['customer_id']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Order {self.order_number} - {self.customer_name} ({self.status})"

    @property
    def is_complete_data(self):
        """Check if all required customer data is provided"""
        return all([
            self.customer_name,
            self.customer_age,
            self.customer_id,
        ])

    @property
    def order_number(self):
        """Generate a human-readable order number"""
        return f"WZ-{self.id.hex[:8].upper()}"


class ServiceOrderCache(models.Model):
    """
    Temporary cache for incomplete service orders

    Stores partial data while the AI assistant collects all required information.
    Automatically cleaned up after successful order creation or timeout.
    """

    # Session identification
    session_key = models.CharField(
        _("Session Key"),
        max_length=255,
        unique=True,
        help_text=_("Unique session identifier for caching")
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text=_("User associated with this cache entry")
    )

    company = models.ForeignKey(
        'company.Company',
        on_delete=models.CASCADE,
        help_text=_("Company this cache entry belongs to")
    )

    # Service being ordered
    service = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        limit_choices_to={'type': 'service', 'is_service_orderable': True},
        blank=True,
        null=True,
        help_text=_("Service being ordered (if selected)")
    )

    # Cached customer data (JSON for flexibility)
    cached_data = models.JSONField(
        _("Cached Data"),
        default=dict,
        help_text=_("Temporarily stored customer information")
    )

    # Metadata
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("When this cache entry was created")
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text=_("When this cache entry was last updated")
    )

    expires_at = models.DateTimeField(
        help_text=_("When this cache entry expires")
    )

    class Meta:
        verbose_name = _("Service Order Cache")
        verbose_name_plural = _("Service Order Cache")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['session_key']),
            models.Index(fields=['user', 'company']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"Cache {self.session_key} - {self.user.username}"

    @property
    def is_expired(self):
        """Check if this cache entry has expired"""
        from django.utils import timezone
        return timezone.now() > self.expires_at

    def get_missing_fields(self):
        """Get list of missing required fields"""
        required_fields = ['customer_name', 'customer_age', 'customer_id', 'customer_phone']
        missing = []

        for field in required_fields:
            if not self.cached_data.get(field):
                missing.append(field)

        return missing

    @property
    def is_complete(self):
        """Check if all required data is cached"""
        return len(self.get_missing_fields()) == 0
