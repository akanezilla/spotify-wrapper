
from django.shortcuts import render

def transition1_rb(request):
    return render(request, 'RainbowMode/transition1.html')

def transition2_rb(request):
    return render(request, 'RainbowMode/transition2.html')

def slideshow_rb(request):
    return render(request, 'RainbowMode/slideShowRB.html')

def top_5_songs_rb(request):
    return render(request, 'RainbowMode/top_5_songs.html')

def top_song_rb(request):
    return render(request, 'RainbowMode/top_song.html')

def top_artist_rb(request):
  return render(request, 'RainbowMode/top_artists.html')

def top_genre_rb(request):
    return render(request, 'RainbowMode/top_genre.html')

def listening_minutes_rb(request):
    return render(request, 'RainbowMode/listening_minutes.html')

def type_of_listener_rb(request):
    return render(request, 'RainbowMode/type_of_listener.html')

def memorable_moment_rb(request):
    return render(request, 'RainbowMode/memorable_moment.html')

def transition1_lm(request):
    return render(request, 'LightMode/transition1.html')

def transition2_lm(request):
    return render(request, 'LightMode/transition2.html')

def slideshow_lm(request):
    return render(request, 'LightMode/slideShowLM.html')

def top_5_songs_lm(request):
    return render(request, 'LightMode/top_5_songs.html')

def top_song_lm(request):
    return render(request, 'LightMode/top_song.html')

def top_artist_lm(request):
  return render(request, 'LightMode/top_artists.html')

def top_genre_lm(request):
    return render(request, 'LightMode/top_genre.html')

def listening_minutes_lm(request):
    return render(request, 'LightMode/listening_minutes.html')

def type_of_listener_lm(request):
    return render(request, 'LightMode/type_of_listener.html')

def memorable_moment_lm(request):
    return render(request, 'LightMode/memorable_moment.html')