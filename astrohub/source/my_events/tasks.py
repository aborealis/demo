"""Celery tasks for posting to social media"""
from celery import shared_task
from facebook import GraphAPI, GraphAPIError
from mysite.settings import DOMAIN, FB_GROUP_ID, FB_GROUP_TOKEN
from .models import Event


@shared_task
def publish_fb_event(instance_id: int):
    """Sends a link to the new event to the Facebook public page"""
    instance = Event.objects.get(id=instance_id)
    print('Sending request to FB...')

    message = (
        f'New event by {instance.entity}.\n\n'
        f'{instance.date.strftime("%d-%b-%Y, %H:%M")} | GMT {instance.timezone}\n\n'
        f'{instance.abstract}\n'
        f'https://{DOMAIN}/events/{instance.pk}/'
    )

    graph = GraphAPI(FB_GROUP_TOKEN)

    try:
        graph.put_object(
            parent_object=str(FB_GROUP_ID),
            connection_name='feed',
            message=message,
            link=f'https://{DOMAIN}/events/{instance.pk}/',
        )

    except GraphAPIError as e:
        print('FB Error', e)
