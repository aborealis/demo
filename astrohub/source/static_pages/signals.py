"""
Signal handler for the database to delete images
not associated with any objects in the database
"""
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
import common.signals as sgn
from .models import Page


@receiver(pre_save, sender=Page)
def delete_old_file_on_update_page(instance, **kwargs):
    """Deletes old image files when the "ImageField" field is updated"""
    sgn.delete_old_file_on_update_common(Page, instance)


@receiver(post_delete, sender=Page)
def delete_file_on_delete_page(instance, **kwargs):
    """Deletes the image file when an object with an image is deleted"""
    sgn.delete_file_on_delete_common(instance)
