"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.sitemaps.views import sitemap
from blog.sitemaps import BlogSitemap
from my_events.sitemaps import EventSitemap
from static_pages.sitemaps import PageSitemap

admin.site.site_header = 'Astrological Events Worldwide'
admin.site.index_title = 'Admin Area'


urlpatterns = [
    path('admin/', admin.site.urls),
    path('events/', include('my_events.urls')),
    path('blog/', include('blog.urls')),
    path('', include('static_pages.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': {
        'blog': BlogSitemap(),
        'events': EventSitemap(),
        'pages': PageSitemap(),
    }},
        name='django.contrib.sitemaps.views.sitemap'),
]
