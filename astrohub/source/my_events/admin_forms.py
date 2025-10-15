"""
Custom forms for displaying various objects
from different tables with user restrictions
"""
from common.custom_forms import EntityRestrictedFormMixin
from .models import Event


class EventCustomForm(EntityRestrictedFormMixin):
    """Custom form for an Event object instance being edited by a user."""
    class Meta:
        model = Event
        fields = '__all__'
