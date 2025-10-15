"""Request dispatcher for various URLs related to blog posts."""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.show_all_posts, name='blog'),
    path('search/', views.show_posts_in_search, name='posts_in_search'),
    path('by/<int:entity_id>/', views.show_posts_by_entity, name='posts_by_entity'),
    path('<slug:slug>/', views.show_chosen_post, name='show_post'),
]
