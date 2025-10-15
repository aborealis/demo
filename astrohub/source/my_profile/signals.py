"""
Database signal handler for deleting images
not associated with any objects in the database
"""

from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
import common.signals as sgn
from .models import Entity


@receiver(pre_save, sender=Entity)
def delete_old_file_on_update(instance, **kwargs):
    """Deletes old image files when the "ImageField" field is updated"""
    sgn.delete_old_file_on_update_common(Entity, instance)


@receiver(post_delete, sender=Entity)
def delete_file_on_delete(instance, **kwargs):
    """Deletes the image file when the object with the image is deleted"""
    sgn.delete_file_on_delete_common(instance)
