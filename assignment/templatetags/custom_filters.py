# assignment/templatetags/custom_filters.py

from django import template
import os
register = template.Library()


@register.filter(name='add_class')
def add_class(value, arg):
    """Add CSS class to form field widget."""
    return value.as_widget(attrs={'class': arg})


@register.filter
def basename(value):
    """Returns the base name of a file path."""
    return os.path.basename(value)


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


