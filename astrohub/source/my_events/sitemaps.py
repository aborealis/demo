"""Sitemap generator https://docs.djangoproject.com/en/4.1/ref/contrib/sitemaps/"""
from django.contrib.sitemaps import Sitemap
from .models import Event

# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# Composite types annotation
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
AnyDbResult = Event


class EventSitemap(Sitemap):
    """Defines a Sitemap object for the events"""
    changefreq = 'yearly'
    priority = 0.5

    def items(self):
        return Event.objects.all()
