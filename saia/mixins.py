"""
Data isolation mixins for multi-tenant SaaS architecture
"""
from django.core.exceptions import PermissionDenied
from django.db import models


class CompanyFilterMixin:
    """
    Mixin to filter querysets by user's company for customer users.
    SAIA admins see all data, customer users see only their company's data.
    """
    
    def get_company_filtered_queryset(self, model_class, user=None):
        """
        Get queryset filtered by company for customer users.
        
        Args:
            model_class: Django model class
            user: User instance (defaults to self._user for AI assistant)
            
        Returns:
            Filtered queryset
        """
        if user is None:
            user = getattr(self, '_user', None)
        
        if not user:
            raise PermissionDenied("User context required for data access")
        
        queryset = model_class.objects.all()
        
        # SAIA admins see all data
        if hasattr(user, 'is_saia_admin') and user.is_saia_admin():
            return queryset
        
        # Customer users see only their company's data
        if hasattr(user, 'is_customer') and user.is_customer and hasattr(user, 'company') and user.company:
            if hasattr(model_class, 'company'):
                return queryset.filter(company=user.company)
            elif model_class.__name__ == 'Transaction':
                # Special case: Transaction gets company through Product
                return queryset.filter(product__company=user.company)
            elif model_class.__name__ == 'InvoiceDetails':
                # Special case: InvoiceDetails gets company through Invoice
                return queryset.filter(invoice__company=user.company)
        
        # Customer without company or other cases - no access
        return queryset.none()
    
    def check_company_access(self, obj, user=None):
        """
        Check if user can access a specific object based on company.
        
        Args:
            obj: Model instance
            user: User instance
            
        Returns:
            bool: True if access allowed
        """
        if user is None:
            user = getattr(self, '_user', None)
        
        if not user:
            return False
        
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

    def filter_by_company(self, request, queryset):
        """
        Filter queryset by user's company for Django admin.

        Args:
            request: Django request object
            queryset: Initial queryset

        Returns:
            Filtered queryset
        """
        user = request.user

        # SAIA admins see all data
        if hasattr(user, 'is_saia_admin') and user.is_saia_admin():
            return queryset

        # Customer users see only their company's data
        if hasattr(user, 'is_customer') and user.is_customer and hasattr(user, 'company') and user.company:
            # Check if the model has a company field
            if hasattr(queryset.model, 'company'):
                return queryset.filter(company=user.company)

        # Default: return empty queryset for safety
        return queryset.none()
