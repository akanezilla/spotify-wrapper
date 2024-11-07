from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from spotify.models import SpotifyProfile

@login_required
def home_view(request):
    try:
        spotify_profile = SpotifyProfile.objects.get(user=request.user)
        is_connected = True
    except SpotifyProfile.DoesNotExist:
        is_connected = False

    print(f"Is connected: {is_connected}")  # Add this line for debugging

    return render(request, 'home/home.html', {
        'username': request.user.username,
        'is_connected': is_connected
    })