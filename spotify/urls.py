from django.urls import path
from . import views

app_name = 'spotify'

urlpatterns = [
   path('connect/', views.spotify_connect, name='spotify_connect'),
    path('callback/', views.spotify_callback, name='spotify_callback'),
    path('data/', views.spotify_data_view, name='spotify_data'),
    path('top-tracks/', views.top_tracks_view, name='top_tracks'),
    path('total-listening-time/', views.total_listening_time_view, name='total_listening_time'),
    path('top-song/', views.top_song_view, name='top_song'),
    path('memorable-moment/', views.memorable_moment_view, name='memorable_moment'),  
    path('RainbowMode/top_5_songs/', views.top_tracks_view, name='top_5_songsRB'),  
    path('RainbowMode/top_artists/', views.top_artists_view, name='top_artistsRB'),  
    path('RainbowMode/type_of_listener/', views.listener_type_view, name='listener_typeRB'),  
    path('', views.home_view, name='home'),
    path('top-genres/', views.top_genre_view, name='top_genres'),
    path('home/', views.home_view, name='home'),
    path('save-wrap/', views.save_wrap, name='save_wrap'),


]