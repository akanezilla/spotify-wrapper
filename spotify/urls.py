from django.urls import path
from . import views

app_name = 'spotify'
urlpatterns = [
    path('connect/', views.spotify_connect, name='spotify_connect'),
    path('callback/', views.spotify_callback, name='spotify_callback'),
]