"""Request dispatcher for various URLs in Static Pages app"""
from django.urls import path
from . import views

urlpatterns = [
    path('<slug:slug>/', views.show_page, name='static_page'),
    path('', views.show_main, name='main_page'),
]
