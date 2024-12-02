from django.urls import path
from . import views

app_name = 'spotify'

urlpatterns = [
    path('connect/', views.spotify_connect, name='spotify_connect'),
    path('callback/', views.spotify_callback, name='spotify_callback'),
    path('data/', views.spotify_data_view, name='spotify_data'),
    path('top-tracks/', views.top_tracks_view, name='top_tracks'),
    path('random-songs/', views.random_songs_view, name='random_songs'),
    path('total-listening-time/', views.total_listening_time_view, name='total_listening_time'),
    path('top-song/', views.top_song_view, name='top_song'),
    path('memorable-moment/', views.memorable_moment_view, name='memorable_moment'),  
    path('RainbowMode/top_5_songs/', views.top_5_songs_rb, name='top_5_songsRB'),  
    path('RainbowMode/top_artists/', views.top_artists_rb, name='top_artistsRB'),  
    path('RainbowMode/type_of_listener/', views.type_of_listenerRB, name='listener_typeRB'),  
    path('save-wrapped/', views.spotify_wrapped_view, name='save-wrapped'),
    path('', views.home_view, name='home'),
    path('top-genres/', views.top_genre_view, name='top_genres'),
    path('save/', views.save_wrap, name='save_wrap'),  # URL for saving a wrap
    path('saved/', views.saved_wraps, name='saved_wraps'),  # URL for displaying saved wraps



]