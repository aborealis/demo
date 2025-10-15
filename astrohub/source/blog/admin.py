"""Django admin panel interface for working with blog articles"""
from django.contrib import admin
from common.admin import get_seo_title_length
from common.admin import EntityRestrictedMixin
from .models import Author, Post
from .admin_forms import PostCustomForm, AuthorCustomForm


DESCRIPTIONS = [
    (
        '<p>Please include "https://" prefix intro the URL field. It should be'
        "a valid link to the author's web page or social profile, where the "
        "readers can contact the author.</p><p>Recommended author's photo size "
        'is 300x300 px.</p>'
    ),
    (
        'A slug is a part of URL of your article, like "https://example.com/slug/"'
    ),
    (
        'A good title for Google - 50-60 characters, and description - 140-160 symbols'
    ),
    (
        'Recommended format - 1200x630, jpg. <br /> An image alt is a text description of an '
        'image used by screen readers and search engines to understand the content of the image'
    ),
    (
        'Use <a href="https://support.typora.io/Markdown-Reference/" '
        'rel="norefferer noopener" target="_blank">markdown syntaxt</a> '
        'for the content of the post and plain text for the abstract'
    ),
]


@admin.register(Author)
class AuthorAdmin(EntityRestrictedMixin):
    """Authors representation in the Django admin panel"""
    form = AuthorCustomForm
    list_display = ['name', 'entity']
    search_fields = ['name']

    fieldsets = [
        (None, {
            'fields': ['entity', 'name', 'image', 'description', 'url'],
            'description': DESCRIPTIONS[0]
        })
    ]


@admin.register(Post)
class PostAdmin(EntityRestrictedMixin):
    """Article list representation in the Django admin panel"""
    form = PostCustomForm
    list_display = ['title', 'author', 'seo_title_length']
    autocomplete_fields = ['author', ]
    search_fields = [
        'title', 'seo_description',
        'seo_title', 'slug', 'content', 'abstract',
    ]

    fieldsets = [
        (None, {
            'fields': ['entity', 'title', 'slug', 'author'],
            'description': DESCRIPTIONS[1]
        }),
        ('SEO Data Search Engines', {
            'fields': ['seo_title', 'seo_description'],
            'description': DESCRIPTIONS[2]
        }),
        ('Post Image', {
            'fields': ['image', 'image_alt'],
            'description': DESCRIPTIONS[3]
        }),
        ('Content', {
            'fields': ['content', 'abstract'],
            'description': DESCRIPTIONS[4]
        }),
        ('Special Characters', {
            'fields': ['include_math', 'include_astrofont']
        }
        ),
    ]

    def seo_title_length(self, post: Post):
        """Evaluates the SEO title and SEO description lengths"""
        return get_seo_title_length(post)
