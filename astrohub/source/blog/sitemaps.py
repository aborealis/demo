"""Sitemap generator: https://docs.djangoproject.com/en/4.1/ref/contrib/sitemaps/"""
from datetime import datetime
from django.contrib.sitemaps import Sitemap
from .models import Post

# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# Composite types annotation
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
AnyDbResult = Post


class BlogSitemap(Sitemap):
    """Defines a Sitemap object for the blog"""
    changefreq = 'yearly'
    priority = 0.5

    def items(self):
        return Post.objects.all()

    def lastmod(self, obj: AnyDbResult) -> datetime:
        """Last modification date"""
        return obj.date_modified
