"""
Functions and classes for amin_forms.py files
in various applications to restrict user access
to certain fields based on their permissions.
"""
from typing import cast
from django.http import HttpRequest
from django import forms
from my_profile.models import User


def form_with_request(form_class, request):
    """
    Returns a form class with the request
    attribute from the HTTP request added
    """

    class EventFormWithRequest(form_class):
        """Overridden form class"""

        def __new__(cls, *args, **kwargs):
            kwargs['request'] = request
            return form_class(*args, **kwargs)

    return EventFormWithRequest


class EntityRestrictedFormMixin(forms.ModelForm):
    """Mixin for hiding the 'entity' field for non-superusers."""

    def __init__(self, *args, **kwargs):
        self.request: HttpRequest = kwargs.pop('request', None)
        is_superuser = self.request and self.request.user.is_superuser
        super().__init__(*args, **kwargs)

        if not is_superuser:
            user = cast(User, self.request.user)
            entity_field = self.fields['entity']
            entity_field.initial = user.entity
            entity_field.widget = entity_field.hidden_widget()
