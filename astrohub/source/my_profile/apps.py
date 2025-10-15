"""Configuration for the my_profile app."""
from django.apps import AppConfig


class MyProfileConfig(AppConfig):
    """Configuration for the my_profile app."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'my_profile'

    def ready(self):
        import my_profile.signals  # pylint: disable=import-outside-toplevel, unused-import
