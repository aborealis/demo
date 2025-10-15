"""Representations of organizations and users tables from the "my_profile" DB table in the Django admin panel"""
from typing import Optional, cast
from django.contrib import admin
from django.http import HttpRequest
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User, Entity


class EntityRestrictedMixin(admin.ModelAdmin):
    """
    Mixin for restricting viewing, modification, and deletion 
    of the organizations (entities), not assosiated with the regular user.
    """

    def has_change_permission(self, request: HttpRequest, obj: Optional[User] = None):
        """Restrict the ability to edit other entities"""
        user = cast(User, request.user)

        if (obj and obj == user.entity) or user.is_superuser:
            return super().has_change_permission(request, obj)

        return False

    def has_delete_permission(self, request: HttpRequest, obj: Optional[User] = None):
        """Restrict the ability to delete any entity"""
        user = cast(User, request.user)

        if user.is_superuser:
            return super().has_delete_permission(request, obj)

        return False

    def get_queryset(self, request):
        """Limit the list of organisation only to those associated with the user's entity"""
        qs = super().get_queryset(request)
        user = cast(User, request.user)

        if user.is_superuser:
            return qs

        entity = cast(Entity, user.entity)
        return qs.filter(pk=entity.pk)


@admin.register(Entity)
class EntityAdmin(EntityRestrictedMixin):
    """
    Admin panel representation for Organization objects.
    Restricts non-superusers from viewing or editing organizations 
    with which they are not associated.
    """

    search_fields = ['name']


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """
    Override the default user representation fields,
    adding an organization relation field to them
    """
    fieldsets = [
        ('Organization', {
            'fields': ('entity',)
        }),
        *DjangoUserAdmin.fieldsets
    ]

    add_fieldsets = [
        (None, {
            'fields': ('entity',),
        }),
        *DjangoUserAdmin.add_fieldsets
    ]
