from django.urls import path
from . import views

app_name = 'spotify'

urlpatterns = [
    path('connect/', views.spotify_connect, name='spotify_connect'),
    path('callback/', views.spotify_callback, name='spotify_callback'),
    path('data/', views.spotify_data_view, name='spotify_data'),
    path('top-tracks/', views.top_tracks_view, name='top_tracks'),
   # path('top-artists/', views.top_artists_view, name='top_artists'),
    path('top-genre/', views.top_genre_view, name='top_genre'),
    path('listener-type/', views.listener_type_view, name='listener_type'),
    path('random-songs/', views.random_songs_view, name='random_songs'),
    path('total-listening-time/', views.total_listening_time_view, name='total_listening_time'),
    path('top-song/', views.top_song_view, name='top_song'),
    path('memorable-moment/', views.memorable_moment_view, name='memorable_moment'),  
    path('RainbowMode/top_5_songs/', views.top_5_songs_rb, name='top_5_songsRB'),  
    path('RainbowMode/top_artists/', views.top_artists_rb, name='top_artistsRB'),  

]