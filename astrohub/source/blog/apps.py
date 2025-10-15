"""Configuration for the blog app."""
from django.apps import AppConfig


class BlogConfig(AppConfig):
    """Configuration for the blog app."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog'

    def ready(self):
        import blog.signals  # pylint: disable=import-outside-toplevel, unused-import
