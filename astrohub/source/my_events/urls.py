"""Request dispatcher for various URLs in the events application"""
from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.show_events_in_search, name='show_events_in_search'),
    path('by/<int:entity_id>/', views.show_events_by_entity,
         name='show_events_by_entity'),
    path('<int:year>/<int:month>/', views.show_filtered_events),
    path('<int:event_id>/', views.show_chosen_event, name='show_chosen_event'),
]
