"""
Sitemap generator https://docs.djangoproject.com/en/4.1/ref/contrib/sitemaps/
"""
from datetime import datetime
from django.contrib.sitemaps import Sitemap
from .models import Page

# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# Composite types annotation
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
AnyDbResult = Page


class PageSitemap(Sitemap):
    """Define Sitemap object for static pages"""
    changefreq = 'yearly'
    priority = 0.5

    def items(self):
        return Page.objects.all().exclude(slug='main')

    def lastmod(self, obj: AnyDbResult) -> datetime:
        """Last modification date"""
        return obj.date_modified
