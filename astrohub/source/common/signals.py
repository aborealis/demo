"""Common functions for signals in each database table"""
import os
from typing import Union
from blog.models import Post, Author
from my_events.models import Event
from my_profile.models import Entity
from static_pages.models import Page

Instance = Union[Post, Author, Event, Entity, Page]


def delete_old_file_on_update_common(model: type[Instance], instance: Instance):
    """Deletes old image files when the "ImageField" field is updated"""
    if not instance.pk:
        return False

    try:
        old_file = model.objects.get(pk=instance.pk).image
    except model.DoesNotExist:
        return False

    new_file = instance.image
    if old_file and not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)

    return None


def delete_file_on_delete_common(instance):
    """
    Deletes the image file when the object with the image is deleted
    """

    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)
