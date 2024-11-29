
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
    return render(request, 'RainbowMode/top_artist.html')

def top_genre_rb(request):
    return render(request, 'RainbowMode/top_genre.html')

def listening_minutes_rb(request):
    return render(request, 'RainbowMode/listening_minutes.html')

def type_of_listener_rb(request):
    return render(request, 'RainbowMode/type_of_listener.html')

def memorable_moment_rb(request):
    return render(request, 'RainbowMode/memorable_moment.html')