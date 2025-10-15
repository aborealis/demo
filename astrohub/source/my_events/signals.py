"""
Database signal handler for deleting images
not associated with any objects in the database
"""
from typing import cast
from django.db.models.signals import pre_save, post_delete, post_save
from django.dispatch import receiver
from celery import Task
import common.signals as sgn
from .models import Event
from .tasks import publish_fb_event


@receiver(pre_save, sender=Event)
def delete_old_file_on_update(instance, **kwargs):
    """Deletes old image files when the "ImageField" field is updated"""
    sgn.delete_old_file_on_update_common(Event, instance)


@receiver(post_delete, sender=Event)
def delete_file_on_delete(instance, **kwargs):
    """Deletes the image file when the object with the image is deleted"""
    sgn.delete_file_on_delete_common(instance)


@receiver(post_save, sender=Event)
def post_to_social_media(instance: Event, created, **kwargs):
    """Publishes a link to the event on social media when the post is first saved"""

    if created:
        task = cast(Task, publish_fb_event)
        task.apply_async((instance.pk,), countdown=30)
