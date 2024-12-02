from django.urls import path
from . import views
from django.views.generic.base import RedirectView
from spotify.views import home_view

urlpatterns = [
    path('RainbowMode/transition1/', views.transition1_rb, name='transition1RB'),
    path('RainbowMode/transition2/', views.transition2_rb, name='transition2RB'),
    path('RainbowMode/slideShowRB/', views.slideshow_rb, name='slideShowRB'),
    path('RainbowMode/top_5_songs/', views.top_5_songs_rb, name='top_5_songsRB'),
    path('RainbowMode/top_song/', views.top_song_rb, name='top_songRB'),
    path('RainbowMode/top_artists/', views.top_artist_rb, name='top_artistsRB'),
    path('RainbowMode/top_genre/', views.top_genre_rb, name='top_genreRB'),
    path('RainbowMode/listening_minutes/', views.listening_minutes_rb, name='listening_minutesRB'),
    path('RainbowMode/type_of_listener/', views.type_of_listener_rb, name='type_of_listenerRB'),
    path('RainbowMode/memorable_moment/', views.memorable_moment_rb, name='memorable_momentRB'),
    path('home/', home_view, name='home')
]