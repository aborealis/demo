"""Events representations in the Django admin panel"""
from django.contrib import admin
from common.admin import get_seo_title_length
from common.admin import EntityRestrictedMixin
from .models import Event
from .admin_forms import EventCustomForm


DESCRIPTIONS = [
    'A good title for Google - 50-60 characters, and description - 140-160 symbols',
    'Recommended image size: 1200 x 630 px.'
]


@admin.register(Event)
class EventAdmin(EntityRestrictedMixin):
    """Event instance representation"""
    form = EventCustomForm
    list_display = ['date', 'title', 'type', 'entity', 'seo_title_length']
    autocomplete_fields = ['entity']
    fieldsets = [
        (None, {
            'fields': [
                'entity', 'title', 'date', 'timezone',
                'type', 'format', 'duration', 'audience'
            ]
        }),
        ('SEO', {
            'fields': ['seo_title', 'seo_description'],
            'description': DESCRIPTIONS[0],
        }),
        ('Event Details', {
            'fields': ['image', 'registration_url', 'description', 'abstract'],
            'description': DESCRIPTIONS[1],
        }),
    ]

    def seo_title_length(self, event: Event):
        """Evaluates the SEO title length"""
        return get_seo_title_length(event)
