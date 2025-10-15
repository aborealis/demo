"""Server responses when accessing the /event/ endpoint"""
from datetime import datetime
from functools import reduce
from operator import or_
from dateutil.relativedelta import relativedelta
import bleach
from markdown import markdown
from django.http import HttpRequest, HttpResponse, Http404
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from my_profile.models import Entity
from static_pages.models import Page
from common.view_funcs import show_events_for_period, show_chosen_events
from .models import Event

PER_PAGE = 10


def show_filtered_events(request: HttpRequest, year: int, month: int) -> HttpResponse:
    """
    Returns a site page with a list of
    events filtered by specified criteria.
    """
    page = Page.objects.filter(slug='main')[0]
    page.title = f'Astrological Events for {month}/{year}'
    page.seo_title = f'Astrological Events for {month}/{year}: Conferences, Classes and Webinars'

    try:
        start_date = datetime(year=year, month=month, day=1)

    except ValueError as exc:
        raise Http404("Post does not exist") from exc

    return show_events_for_period(
        request,
        start_date=start_date,
        end_date=start_date + relativedelta(months=1),
        page=page,
        per_page=PER_PAGE,
    )


def show_events_in_search(request: HttpRequest) -> HttpResponse:
    """Returns a site page with a list of events resulting from a search."""
    search = request.GET.get('s')
    if not search:
        return redirect('/')

    page = Page.objects.filter(slug='main')[0]
    page.title = f'Search Results for {search}'
    page.seo_title = 'lalala'

    queries = [
        Q(title__icontains=search),
        Q(description__icontains=search),
        Q(abstract__icontains=search),
        Q(entity__name__icontains=search)
    ]

    events = Event.objects.filter(reduce(or_, queries)).order_by('date')
    return show_chosen_events(request, events, page, PER_PAGE)


def show_events_by_entity(request: HttpRequest, entity_id: int) -> HttpResponse:
    """
    Returns a site page with a list of events 
    created by the specified organization.
    """
    page = Page.objects.filter(slug='main')[0]
    entity = get_object_or_404(Entity, id=entity_id)

    page.title = f'Astrological Events by {entity.name}'
    page.seo_title = f'Astrological Events by {entity.name}: Conferences, Classes and Webinars'

    events = Event.objects.filter(entity_id=entity_id).order_by('date')
    return show_chosen_events(request, events, page, PER_PAGE)


def show_chosen_event(request: HttpRequest, event_id: int) -> HttpResponse:
    """Returns the page of the selected event."""
    event = get_object_or_404(Event, id=event_id)

    entity_website: str = event.entity.website
    registration_url: str = event.registration_url

    if entity_website and not entity_website.startswith('https://'):
        event.entity.website = 'https://' + entity_website

    if registration_url and not registration_url.startswith('https://'):
        event.registration_url = 'https://' + registration_url

    html = markdown(event.description, extensions=['tables', 'footnotes']).replace(
        '<table>',
        '<div class="table-responsive"><table class="table table-striped table-hover">'
    ).replace('</table>', '</table></div>')

    allowed_tags = list(bleach.sanitizer.ALLOWED_TAGS) + [
        'p', 'div', 'span', 'table', 'thead', 'tbody', 'tr', 'th', 'td',
        'a', 'img', 'ul', 'ol', 'li', 'strong', 'em', 'blockquote', 'code',
        'pre', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'
    ]
    allowed_attributes = {
        '*': ['class', 'style'],
        'a': ['href', 'title', 'rel'],
        'img': ['src', 'alt', 'title']
    }

    event.description = bleach.clean(
        html, tags=allowed_tags, attributes=allowed_attributes)

    context = {
        'page': event,
        'page_type': 'event',
        'domain': request.build_absolute_uri('/')[:-1],
    }

    return render(request, 'page_design/page.html', context)
