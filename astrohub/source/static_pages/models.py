"""Database table structure of the site static pages"""
from django.db import models


class Page(models.Model):
    """Static page model"""
    title = models.CharField(max_length=100)
    seo_title = models.CharField(max_length=100)
    seo_description = models.CharField(max_length=200)
    image = models.ImageField(upload_to="static/img/page/", blank=False)
    image_alt = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    date_published = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    include_astrofont = models.BooleanField(default=False)
    include_math = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f'{self.title}'

    def get_absolute_url(self):
        """Returns the absolute path to the page"""
        if self.slug == 'main':
            return '/'

        return f"/{self.slug}/"
