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

    path('LightMode/transition1/', views.transition1_lm, name='transition1LM'),
    path('LightMode/transition2/', views.transition2_lm, name='transition2LM'),
    path('LightMode/slideShowLM/', views.slideshow_lm, name='slideShowLM'),
    path('LightMode/top_5_songs/', views.top_5_songs_lm, name='top_5_songsLM'),
    path('LightMode/top_song/', views.top_song_lm, name='top_songLM'),
    path('LightMode/top_artists/', views.top_artist_lm, name='top_artistsLM'),
    path('LightMode/top_genre/', views.top_genre_lm, name='top_genreLM'),
    path('LightMode/listening_minutes/', views.listening_minutes_lm, name='listening_minutesLM'),
    path('LightMode/type_of_listener/', views.type_of_listener_lm, name='type_of_listenerLM'),
    path('LightMode/memorable_moment/', views.memorable_moment_lm, name='memorable_momentLM'),

    path('DarkMode/transition1/', views.transition1_dm, name='transition1DM'),
    path('DarkMode/transition2/', views.transition2_dm, name='transition2DM'),
    path('DarkMode/slideShowDM/', views.slideshow_dm, name='slideShowDM'),
    path('DarkMode/top_5_songs/', views.top_5_songs_dm, name='top_5_songsDM'),
    path('DarkMode/top_song/', views.top_song_dm, name='top_songDM'),
    path('DarkMode/top_artists/', views.top_artist_dm, name='top_artistDM'),
    path('DarkMode/top_genre/', views.top_genre_dm, name='top_genreDM'),
    path('DarkMode/listening_minutes/', views.listening_minutes_dm, name='listening_minutesDM'),
    path('DarkMode/type_of_listener/', views.type_of_listener_dm, name='type_of_listenerDM'),
    path('DarkMode/memorable_moment/', views.memorable_moment_dm, name='memorable_momentDM'),
]
