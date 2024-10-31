from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('connect/', views.spotify_connect, name='spotify_connect'),
    path('callback/', views.spotify_callback, name='spotify_callback'),
]