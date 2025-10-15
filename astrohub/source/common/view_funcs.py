"""Common functions for views in different applications"""
from datetime import datetime
from functools import reduce
from operator import or_
from django.http import HttpRequest, HttpResponse
from django.core.paginator import Paginator, Page
from django.shortcuts import render
from django.db.models import Min, Max, Q, QuerySet
from static_pages import models
from my_events.models import Event


def get_items_to_show_per_page(request: HttpRequest,
                               all_items: QuerySet,
                               per_page: int = 10) -> Page:
    """Returns posts to display on the current page"""
    paginator = Paginator(
        list(all_items), per_page
    )

    try:
        page_number = int(request.GET.get('p', 1))
    except ValueError:
        page_number = 1

    if page_number not in paginator.page_range:
        page_number = 1

    return paginator.get_page(page_number)


def show_chosen_events(request: HttpRequest,
                       events: QuerySet[Event],
                       page: models.Page,
                       per_page: int = 10,
                       ) -> HttpResponse:
    """Returns a page with a list of specified events"""
    events_per_current_page = get_items_to_show_per_page(
        request, events, per_page)

    # Separately define all years of saved events
    # for filtering by these years
    min_max_dates: dict[str, datetime] = Event.objects.aggregate(
        min_date=Min('date'),
        max_date=Max('date')
    )
    min_year = min_max_dates['min_date'].year if min_max_dates['min_date'] else None
    max_year = min_max_dates['max_date'].year if min_max_dates['max_date'] else None

    if min_year is not None and max_year is not None:
        years = list(range(min_year, max_year + 1))
    else:
        years = []

    context = {
        'page_type': 'list_of_events',
        "page": page,
        'all_posts': events_per_current_page,
        "domain": request.build_absolute_uri('/')[:-1],
        'years': years,
    }

    return render(request, 'page_design/page.html', context)


def show_events_for_period(request: HttpRequest,
                           start_date: datetime,
                           end_date: datetime,
                           page: models.Page,
                           per_page: int = 10,
                           ) -> HttpResponse:
    """Returns a page with a list of events for a given period"""
    events = Event.objects.all().filter(
        date__gt=start_date,
        date__lte=end_date
    ).order_by('date')

    event_type = request.GET.get('t')
    event_format = request.GET.get('f')
    event_duration = request.GET.get('d')
    event_audience = request.GET.get('a')

    if event_type in ['webinar', 'conference', 'course', 'other']:
        events = events.filter(type=event_type)

    if event_format in ['online', 'in_person', 'hybrid']:
        events = events.filter(format=event_format)

    if event_duration in ['oneday', 'multiday']:
        events = events.filter(duration=event_duration)

    if event_audience in ['newbies', 'advanced']:
        queries = [
            Q(audience=event_audience),
            Q(audience='any'),
        ]
        events = events.filter(reduce(or_, queries))

    return show_chosen_events(request, events, page, per_page)
