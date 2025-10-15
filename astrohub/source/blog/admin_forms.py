"""
Custom forms for displaying various objects
from different tables with user restrictions
"""
from django import forms
from common.custom_forms import EntityRestrictedFormMixin
from .models import Post, Author


class PostCustomForm(EntityRestrictedFormMixin, forms.ModelForm):
    """Custom form for a blog post instance being edited by a user."""
    class Meta:
        model = Post
        fields = '__all__'


class AuthorCustomForm(EntityRestrictedFormMixin, forms.ModelForm):
    """Custom form for the author instance being edited by a user."""
    class Meta:
        model = Author
        fields = '__all__'
