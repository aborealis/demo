"""Server responses when accessing the /blog/ endpoint"""
from functools import reduce
from operator import or_
import bleach
from markdown import markdown
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, HttpResponse
from django.db.models import Q, QuerySet
from common.view_funcs import get_items_to_show_per_page
from static_pages.models import Page
from my_profile.models import Entity
from .models import Post

PER_PAGE = 10


def __show_chosen_posts(request: HttpRequest,
                        posts: QuerySet[Post],
                        page: Page,
                        per_page: int = PER_PAGE,
                        ) -> HttpResponse:
    """Returns a page with a list of specified posts"""
    posts_per_current_page = get_items_to_show_per_page(
        request, posts, per_page
    )

    context = {
        'page_type': 'list_of_posts',
        "page": page,
        'all_posts': posts_per_current_page,
        "domain": request.build_absolute_uri('/')[:-1],
    }

    return render(request, 'page_design/page.html', context)


def show_all_posts(request: HttpRequest) -> HttpResponse:
    """Returns a list of all blog articles"""
    posts = Post.objects.all().order_by('-date_published')
    page = Page.objects.all().filter(slug='blog')[0]

    return __show_chosen_posts(request, posts, page, PER_PAGE)


def show_posts_in_search(request: HttpRequest) -> HttpResponse:
    """Returns a site page with a list of posts from the search results"""
    search = request.GET.get('s')
    if not search:
        return redirect('/blog/')

    page = Page.objects.filter(slug='blog')[0]
    page.title = f'Search Results for {search}'

    queries = [
        Q(title__icontains=search),
        Q(content__icontains=search),
        Q(abstract__icontains=search),
        Q(entity__name__icontains=search)
    ]

    posts = Post.objects.filter(
        reduce(or_, queries)).order_by('-date_published')

    return __show_chosen_posts(request, posts, page, PER_PAGE)


def show_posts_by_entity(request: HttpRequest, entity_id: int) -> HttpResponse:
    """
    Returns a site page with a list of posts
    created by the given organization (entity).
    """
    page = Page.objects.filter(slug='blog')[0]
    entity = get_object_or_404(Entity, id=entity_id)

    page.title = f'Astrological Posts by {entity.name}'
    page.seo_title = f'Astrological Posts by {entity.name}: Conferences, Classes and Webinars'

    posts = Post.objects.filter(
        entity_id=entity_id
    ).order_by('-date_published')

    return __show_chosen_posts(request, posts, page, PER_PAGE)


def show_chosen_post(request: HttpRequest, slug: int) -> HttpResponse:
    """Returns the page of the selected post"""
    post = get_object_or_404(Post, slug=slug)
    entity_website: str = post.entity.website

    if entity_website and not entity_website.startswith('https://'):
        post.entity.website = 'https://' + entity_website

    if post.author.url and not post.author.url.startswith('https://'):
        post.author.url = 'https://' + post.author.url

    html = markdown(post.content, extensions=['tables', 'footnotes']).replace(
        '<table>',
        '<div class="table-responsive"><table class="table table-striped table-hover">'
    ).replace('</table>', '</table></div>')

    allowed_tags = list(bleach.sanitizer.ALLOWED_TAGS) + [
        'p', 'div', 'span', 'table', 'thead', 'tbody', 'tr', 'th', 'td',
        'a', 'img', 'ul', 'ol', 'li', 'strong', 'em', 'blockquote', 'code',
        'pre', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    ]

    allowed_attributes = {
        '*': ['class'],
        'a': ['href', 'title', 'rel'],
        'img': ['src', 'alt', 'title']
    }

    post.content = bleach.clean(
        html,
        tags=allowed_tags,
        attributes=allowed_attributes,
        protocols=['http', 'https', 'mailto'],
    )

    context = {
        'page': post,
        'page_type': 'post',
        'domain': request.build_absolute_uri('/')[:-1],
    }

    return render(request, 'page_design/page.html', context)
