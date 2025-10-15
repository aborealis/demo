"""
Database signal handler for deleting images not associated with any 
objects in the database, and also for posting events to Facebook
"""
from django.db.models.signals import pre_save, post_delete, post_save
from django.dispatch import receiver
from facebook import GraphAPI, GraphAPIError
import common.signals as sgn
from mysite.settings import DOMAIN, FB_GROUP_ID, FB_GROUP_TOKEN
from .models import Post, Author


def publish_fb_post(instance: Post, **kwargs):
    """Sends a link to the new post to the Facebook public page"""
    message = (
        f'New post by {instance.entity}.'
        f'{instance.abstract}\n'
        f'https://{DOMAIN}/blog/{instance.slug}/'
    )

    graph = GraphAPI(FB_GROUP_TOKEN)
    try:
        graph.put_object(
            parent_object=str(FB_GROUP_ID),
            connection_name='feed',
            message=message,
            link=f'https://{DOMAIN}/blog/{instance.slug}/',
        )

    except GraphAPIError as e:
        print('Facebook Error:', e)


@receiver(pre_save, sender=Post)
def delete_old_file_on_update_post(instance, **kwargs):
    """Deletes old image files when the "ImageField" is updated"""
    sgn.delete_old_file_on_update_common(Post, instance)


@receiver(post_delete, sender=Post)
def delete_file_on_delete_post(instance, **kwargs):
    """Deletes the image file when the object with the image is deleted"""
    sgn.delete_file_on_delete_common(instance)


@receiver(pre_save, sender=Author)
def delete_old_file_on_update_author(instance, **kwargs):
    """Deletes old image files when the "ImageField" field is updated"""
    sgn.delete_old_file_on_update_common(Author, instance)


@receiver(post_delete, sender=Author)
def delete_file_on_delete_author(instance, **kwargs):
    """Deletes the image file when the object with the image is deleted"""
    sgn.delete_file_on_delete_common(instance)


@receiver(post_save, sender=Post)
def post_to_social_media(instance, created, **kwargs):
    """Publishes a link to the post on social media when the post is first saved"""
    if created:
        publish_fb_post(instance, **kwargs)
