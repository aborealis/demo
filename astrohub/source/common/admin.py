"""Common functions classes for admin.py files"""
from typing import Optional, Union, cast
from django.contrib import admin
from django.http import HttpRequest
from django.utils.html import format_html
from markdown import markdown
from common.custom_forms import form_with_request
from my_profile.models import User
from my_events.models import Event
from blog.models import Post
from static_pages.models import Page

Instance = Union[Event, Post, Page]


def estimate_length(text: str, min_len: int, max_len: int) -> str:
    """
    Evaluates whether the text length is within the 
    required range and returns an appropriate response. 
    Used for displaying objects in the Django admin panel.
    """
    length = len(text)

    if length < min_len:
        return f'Too short ({length} not in {min_len}..{max_len})'

    if length > max_len:
        return f'Too long ({length} not in {min_len}..{max_len})'

    return '<span style="color:green;">OK</span>'


def get_seo_title_length(instance: Instance) -> str:
    """Evaluates the SEO title length"""
    seo_title = instance.seo_title
    meta = instance.seo_description

    result = f'* Title: {estimate_length(seo_title, 50, 60)}\n'
    result += f'* Meta: {estimate_length(meta, 140, 160)}\n'
    result = format_html(markdown(result))

    return result


class EntityRestrictedMixin(admin.ModelAdmin):
    """
    Mixin for restricting the modification and deletion 
    of the object (Event or Posts) for non-superusers.
    """

    def _check_permissions(self, request: HttpRequest, obj: Optional[User] = None) -> bool:
        """Check if the user has permissions to modify the object"""
        user = cast(User, request.user)
        return (obj and obj.entity == user.entity) or user.is_superuser

    def has_change_permission(self, request: HttpRequest, obj: Optional[User] = None):
        """Restrict the ability to edit events/posts associated with other entities"""
        return (
            False if not self._check_permissions(request, obj)
            else super().has_change_permission(request, obj)
        )

    def has_delete_permission(self, request: HttpRequest, obj: Optional[User] = None):
        """Restrict the ability to delete events/posts associated with other entities"""
        return (
            False if not self._check_permissions(request, obj)
            else super().has_delete_permission(request, obj)
        )

    def get_form(self, request, obj=None, change=False, **kwargs):
        """
        Override the form by inserting the user's current organization
        into the entity/post form and hiding this field from view
        """
        form_class = super().get_form(request, obj, **kwargs)
        return form_with_request(form_class, request)

    def get_queryset(self, request):
        """Limit the list of events/posts only to those associated with the user's entity"""
        qs = super().get_queryset(request)
        user = cast(User, request.user)

        if user.is_superuser:
            return qs
        return qs.filter(entity=user.entity)
