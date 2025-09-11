from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin

from django.utils.translation import gettext_lazy as _

from .models import User


# Register your models here.

# class InlineUserAIPermissions(admin.TabularInline):
#     model = UserAIPermissions


# class ExtendGroupAdmin(GroupAdmin):
#     fieldsets = (
#         (
#             None,
#             {
#                 "fields": ("name",),
#             },
#         ),
#         (
#             None,
#             {
#                 "fields": ("permissions",),
#
#             },
#         ),
#
#     )


class ExtendUserAdmin(UserAdmin):
    # inlines = [InlineUserAIPermissions, ]
    fieldsets = [
        (
            None,
            {
                "fields": (
                    "username",
                    "password",
                )
            },
        ),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (
            _("Company & Branch"),
            {
                "fields":
                    (
                        "branch",
                        "company",
                    ),
            },
        ),
        # NEW: Add User Type section
        (
            _("User Type"),
            {
                "fields": ("is_customer",),
                "description": _("Customer users can only access their company's data and AI assistant.")
            },
        ),
        # (
        #     _("AI Permission"),
        #     {
        #         "fields":
        #             (
        #                 "useraipermissions",
        #             ),
        #     },
        # ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        # (
        #     _("Groups"),
        #     {
        #         "fields": ("groups",),
        #     },
        # ),
        # (
        #     _("Permissions"),
        #     {
        #         "fields": ("user_permissions",),
        #     },
        # ),
        (
            _("Important_dates"),
            {
                "fields": (
                    "last_login",
                    "date_joined",
                )
            },
        ),
    ]

    # NEW: Add to list display and filtering
    list_display = ('username', 'email', 'first_name', 'last_name', 'company', 'is_customer', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'is_customer', 'company')

    # NEW: Override get_queryset for admin filtering
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if hasattr(request.user, 'is_customer') and request.user.is_customer:
            # Customer users cannot see other users in admin
            return qs.filter(id=request.user.id)
        return qs


admin.site.register(User, ExtendUserAdmin)
# admin.site.unregister(Group)
# admin.site.register(Group, ExtendGroupAdmin)
