from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from company.models import Company, Branch


# Create your models here.

class User(AbstractUser):
    company = models.ForeignKey(Company, blank=True, null=True, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, blank=True, null=True, on_delete=models.CASCADE)

    # NEW: Add customer role field
    is_customer = models.BooleanField(
        _("Customer User"),
        default=False,
        help_text=_("Designates whether this user is a customer (not SAIA admin).")
    )

    def __str__(self):
        return self.username

    # NEW: Helper methods
    def is_saia_admin(self):
        """Check if user is SAIA admin (staff but not customer)"""
        return self.is_staff and not self.is_customer

    def can_access_admin(self):
        """Check if user can access Django admin"""
        # Both SAIA admins and customer users can access admin
        # Customer users will have limited access via get_queryset filtering
        return self.is_staff


# class UserAIPermissions(models.Model):
#     user = models.OneToOneField(User, related_name='ai_perm', on_delete=models.CASCADE)
#     can_create_threads = models.BooleanField(_("Can Create Threads"), default=False)
#     can_view_threads = models.BooleanField(_("Can View Threads"), default=False)
#     can_create_messages = models.BooleanField(_("Can Create Messages"), default=False)
#     can_view_messages = models.BooleanField(_("Can View Messages"), default=False)
#
#     class Meta:
#         verbose_name = "User AI Permission"
#         verbose_name_plural = "User AI Permissions"
