"""Django admin panel interface for working with static site pages"""
from django.contrib import admin
from common.admin import get_seo_title_length
from .models import Page


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    """Representation of a static site page in the Django admin panel"""
    list_display = ['title', 'seo_title_length']

    def seo_title_length(self, page: Page):
        """
        Evaluates the SEO title length
        """
        return get_seo_title_length(page)
