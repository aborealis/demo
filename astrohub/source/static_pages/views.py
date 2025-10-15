"""Server responses when accessing static page endpoints"""
from dateutil.relativedelta import relativedelta
from django.http import HttpRequest, HttpResponse
from django.utils import timezone
from django.shortcuts import get_object_or_404, render
from common import view_funcs
from .models import Page


PER_PAGE = 10


def show_main(request: HttpRequest) -> HttpResponse:
    """Returns the site's main page content"""
    start_date = timezone.now()

    return view_funcs.show_events_for_period(
        request,
        start_date=start_date,
        end_date=start_date + relativedelta(years=10),
        page=Page.objects.filter(slug='main')[0],
        per_page=PER_PAGE,
    )


def show_page(request: HttpRequest, slug: str) -> HttpResponse:
    """Returns the site's static page content"""
    page = get_object_or_404(Page, slug=slug)

    context = {
        'page': page,
        'page_type': 'page',
        'domain': request.build_absolute_uri('/')[:-1],
    }

    return render(request, 'page_design/page.html', context)
