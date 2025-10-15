"""
Simple custom functions to use as shortcuts in templates
"""
from django import template
register = template.Library()


@register.simple_tag
def define(val=None):
    """
    Creates a tag of the form
    {% define 'value' as my_value %}
    """
    return val


@register.filter
def sub(value, arg):
    """
    Subtracts the arg from the value
    """
    return int(value) - int(arg)


@register.filter
def absolute(value):
    """
    Returns the modulus of a number
    """
    return abs(value)
