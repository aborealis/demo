"""Configuration for the my_event app."""
from django.apps import AppConfig


class MyEventsConfig(AppConfig):
    """Configuration for the my_event app."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'my_events'

    def ready(self):
        import my_events.signals  # pylint: disable=import-outside-toplevel, unused-import
