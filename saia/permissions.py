"""
Custom permissions for SAIA Business Management System

This module provides custom permission functions for AI assistants and other components.
It integrates with Django's permission system while providing additional business logic.
"""

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied


def ensure_ai_permissions_exist():
    """
    Create custom AI assistant permissions if they don't exist.
    This should be called during app initialization or migrations.
    """
    from django.contrib.auth.models import User
    
    # Get or create content type for User (we'll use this for AI permissions)
    user_content_type = ContentType.objects.get_for_model(User)
    
    # Define custom AI permissions (only the ones actually used)
    ai_permissions = [
        ('can_view_product', 'Can view products'),
        ('can_add_product', 'Can add products'),
        ('can_change_product', 'Can change products'),
        ('can_delete_product', 'Can delete products'),
        ('can_view_company', 'Can view companies'),
        ('can_add_company', 'Can add companies'),
        ('can_change_company', 'Can change companies'),
        ('can_delete_company', 'Can delete companies'),
        ('can_view_invoice', 'Can view invoices'),
        ('can_add_invoice', 'Can add invoices'),
        ('can_change_invoice', 'Can change invoices'),
        ('can_delete_invoice', 'Can delete invoices'),
        ('can_view_invoice_details', 'Can view invoice details'),
        ('can_add_invoice_details', 'Can add invoice details'),
        ('can_change_invoice_details', 'Can change invoice details'),
        ('can_delete_invoice_details', 'Can delete invoice details'),
        ('can_view_transaction', 'Can view transactions'),
        ('can_add_transaction', 'Can add transactions'),
        ('can_change_transaction', 'Can change transactions'),
        ('can_add_branch', 'Can add branches'),
        ('can_change_branch', 'Can change branches'),
        ('can_delete_branch', 'Can delete branches'),
    ]
    
    created_permissions = []
    for codename, name in ai_permissions:
        permission, created = Permission.objects.get_or_create(
            codename=codename,
            content_type=user_content_type,
            defaults={'name': name}
        )
        if created:
            created_permissions.append(permission)
    
    return created_permissions


def assign_customer_permissions(user):
    """
    Assign basic permissions to a customer user.
    
    Args:
        user: User instance to assign permissions to
    """
    if not hasattr(user, 'is_customer') or not user.is_customer:
        return
    
    # Ensure permissions exist
    ensure_ai_permissions_exist()
    
    # Basic permissions for customer users
    basic_permissions = [
        'can_view_product',
        'can_add_product', 
        'can_change_product',
        'can_view_company',
        'can_view_invoice',
        'can_add_invoice',
        'can_change_invoice',
        'can_view_invoice_details',
        'can_add_invoice_details',
        'can_change_invoice_details',
        'can_view_transaction',
        'can_add_transaction',
        'can_change_transaction',
    ]
    
    from django.contrib.auth.models import User
    user_content_type = ContentType.objects.get_for_model(User)
    
    for codename in basic_permissions:
        try:
            permission = Permission.objects.get(
                codename=codename,
                content_type=user_content_type
            )
            user.user_permissions.add(permission)
        except Permission.DoesNotExist:
            print(f"Warning: Permission {codename} does not exist")


def assign_admin_permissions(user):
    """
    Assign full permissions to a SAIA admin user.
    
    Args:
        user: User instance to assign permissions to
    """
    if not user.is_staff:
        return
    
    # Ensure permissions exist
    ensure_ai_permissions_exist()
    
    # Admin users get all permissions
    from django.contrib.auth.models import User
    user_content_type = ContentType.objects.get_for_model(User)
    
    ai_permissions = Permission.objects.filter(content_type=user_content_type)
    user.user_permissions.add(*ai_permissions)


def check_company_access(user, obj):
    """
    Check if user can access an object based on company filtering.
    
    Args:
        user: User instance
        obj: Model instance to check access for
        
    Returns:
        bool: True if access is allowed
    """
    # SAIA admins can access everything
    if hasattr(user, 'is_saia_admin') and user.is_saia_admin():
        return True
    
    # Customer users can only access their company's data
    if hasattr(user, 'is_customer') and user.is_customer and hasattr(user, 'company') and user.company:
        if hasattr(obj, 'company'):
            return obj.company == user.company
        elif hasattr(obj, 'product') and hasattr(obj.product, 'company'):
            return obj.product.company == user.company
        elif hasattr(obj, 'invoice') and hasattr(obj.invoice, 'company'):
            return obj.invoice.company == user.company
    
    return False


def user_has_ai_permission(user, permission_codename):
    """
    Check if user has a specific AI permission.
    
    Args:
        user: User instance
        permission_codename: Permission codename to check
        
    Returns:
        bool: True if user has permission
    """
    # Superusers have all permissions
    if user.is_superuser:
        return True
    
    # Check if user has the specific permission
    from django.contrib.auth.models import User
    user_content_type = ContentType.objects.get_for_model(User)
    
    try:
        permission = Permission.objects.get(
            codename=permission_codename,
            content_type=user_content_type
        )
        return user.has_perm(f'{user_content_type.app_label}.{permission_codename}')
    except Permission.DoesNotExist:
        return False


# Convenience functions for common permission checks
def can_view_product(user):
    """Check if user can view products"""
    return user_has_ai_permission(user, 'can_view_product')

def can_add_product(user):
    """Check if user can add products"""
    return user_has_ai_permission(user, 'can_add_product')

def can_change_product(user):
    """Check if user can change products"""
    return user_has_ai_permission(user, 'can_change_product')

def can_view_company(user):
    """Check if user can view companies"""
    return user_has_ai_permission(user, 'can_view_company')

def can_view_invoice(user):
    """Check if user can view invoices"""
    return user_has_ai_permission(user, 'can_view_invoice')


# AI Assistant Thread Security Functions
def ai_assistant_can_view_thread(user, thread, **kwargs):
    """
    SECURITY CRITICAL: Custom thread permission that enforces context separation.

    Admin and customer threads are completely isolated by assistant_id:
    - Customer users can only see threads created with their company-specific assistant
    - Admin users can only see threads created with ProductAIAssistant or company-specific assistants
    - Threads are also filtered by user ownership
    """
    # Superusers can see everything
    if user.is_superuser:
        return True

    # User must own the thread
    if thread.created_by != user:
        return False

    # CRITICAL: Enforce context separation by assistant_id
    from product.ai_assistants import ProductAIAssistant
    from product.assistants import COMPANY_ASSISTANTS

    # Customer users can see their company-specific assistant threads
    if hasattr(user, 'is_customer') and user.is_customer:
        # Allow company-specific assistant threads
        if thread.assistant_id in COMPANY_ASSISTANTS:
            return True

        # Allow company-specific assistant threads if user belongs to that company
        if hasattr(user, 'company') and user.company:
            company_assistant_id = user.company.get_company_assistant_id()
            if company_assistant_id and thread.assistant_id == company_assistant_id:
                return True

        # Also allow legacy assistant IDs for backward compatibility
        legacy_assistant_ids = ['hybrid_customer_assistant']
        if thread.assistant_id in legacy_assistant_ids:
            return True

        return False

    # Admin users can see system admin assistant threads and company-specific assistant threads
    else:
        return thread.assistant_id == ProductAIAssistant.id or thread.assistant_id in COMPANY_ASSISTANTS


def ai_assistant_can_create_thread(user, **kwargs):
    """
    Allow thread creation for authenticated users.
    Context separation is enforced by setting the correct assistant_id when creating.
    """
    return user.is_authenticated


def ai_assistant_can_update_thread(user, thread, **kwargs):
    """
    Allow thread updates only if user can view the thread (enforces same security rules).
    """
    return ai_assistant_can_view_thread(user, thread, **kwargs)


def ai_assistant_can_delete_thread(user, thread, **kwargs):
    """
    Allow thread deletion only if user can view the thread (enforces same security rules).
    """
    return ai_assistant_can_view_thread(user, thread, **kwargs)


def ai_assistant_can_create_message(user, thread, **kwargs):
    """
    Allow message creation only if user can view the thread (enforces same security rules).
    """
    return ai_assistant_can_view_thread(user, thread, **kwargs)


def ai_assistant_can_run_assistant(assistant_cls, user, **kwargs):
    """
    SECURITY CRITICAL: Control which users can run which AI assistants.
    This enforces complete context separation between customer and admin users.
    """
    # Superusers can run any assistant
    if user.is_superuser:
        return True

    # Import assistant classes to check IDs
    from product.ai_assistants import ProductAIAssistant
    from product.assistants import COMPANY_ASSISTANTS

    # Customer users can run their company-specific assistant
    if hasattr(user, 'is_customer') and user.is_customer:
        # Allow company-specific assistant if user belongs to that company
        if hasattr(user, 'company') and user.company:
            company_assistant_id = user.company.get_company_assistant_id()
            if company_assistant_id and assistant_cls.id == company_assistant_id:
                return True

        return False

    # Admin/staff users can run system admin assistant and company-specific assistants
    elif user.is_staff:
        return assistant_cls.id == ProductAIAssistant.id or assistant_cls.id in COMPANY_ASSISTANTS

    # All other users have no access
    return False

# Additional convenience functions for commonly used permissions
def can_add_invoice(user):
    """Check if user can add invoices"""
    return user_has_ai_permission(user, 'can_add_invoice')

def can_view_invoice_details(user):
    """Check if user can view invoice details"""
    return user_has_ai_permission(user, 'can_view_invoice_details')

def can_add_invoice_details(user):
    """Check if user can add invoice details"""
    return user_has_ai_permission(user, 'can_add_invoice_details')

def can_view_transaction(user):
    """Check if user can view transactions"""
    return user_has_ai_permission(user, 'can_view_transaction')

def can_add_transaction(user):
    """Check if user can add transactions"""
    return user_has_ai_permission(user, 'can_add_transaction')

def can_change_invoice_details(user):
    """Check if user can change invoice details"""
    return user_has_ai_permission(user, 'can_change_invoice_details')

def can_delete_product(user):
    """Check if user can delete products"""
    return user_has_ai_permission(user, 'can_delete_product')

def can_add_company(user):
    """Check if user can add companies"""
    return user_has_ai_permission(user, 'can_add_company')

def can_change_company(user):
    """Check if user can change companies"""
    return user_has_ai_permission(user, 'can_change_company')

def can_delete_company(user):
    """Check if user can delete companies"""
    return user_has_ai_permission(user, 'can_delete_company')

def can_add_branch(user):
    """Check if user can add branches"""
    return user_has_ai_permission(user, 'can_add_branch')

def can_change_branch(user):
    """Check if user can change branches"""
    return user_has_ai_permission(user, 'can_change_branch')

def can_delete_branch(user):
    """Check if user can delete branches"""
    return user_has_ai_permission(user, 'can_delete_branch')

def can_change_invoice(user):
    """Check if user can change invoices"""
    return user_has_ai_permission(user, 'can_change_invoice')

def can_delete_invoice(user):
    """Check if user can delete invoices"""
    return user_has_ai_permission(user, 'can_delete_invoice')

def can_delete_invoice_details(user):
    """Check if user can delete invoice details"""
    return user_has_ai_permission(user, 'can_delete_invoice_details')
