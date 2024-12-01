from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from spotify.models import SpotifyProfile

@login_required
def home_view(request):
    try:
        spotify_profile = SpotifyProfile.objects.get(user=request.user)
        is_connected = spotify_profile.spotify_token is not None
    except SpotifyProfile.DoesNotExist:
        is_connected = False

    return render(request, 'home/home.html', {
        'username': request.user.username,
        'is_connected': is_connected
    })

@login_required
def about_view(request):
    return render(request, 'home/about.html')

@login_required
def contact(request):
    return render(request, 'home/contact.html')

