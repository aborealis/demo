"""Configuration for the static page app"""
from django.apps import AppConfig


class StaticPagesConfig(AppConfig):
    """Configuration for the static page app"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'static_pages'

    def ready(self):
        import static_pages.signals  # pylint: disable=import-outside-toplevel, unused-import
