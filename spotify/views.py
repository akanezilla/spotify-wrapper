gitfrom django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from spotipy.oauth2 import SpotifyOAuth
from django.conf import settings
from .models import SpotifyProfile
from django.utils import timezone

@login_required
def spotify_connect(request):
    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI,
        scope="user-read-email user-top-read user-read-recently-played"
    )
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@login_required
def spotify_callback(request):
    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI,
        scope="user-read-email user-top-read user-read-recently-played"
    )
    code = request.GET.get('code')
    token_info = sp_oauth.get_access_token(code)

    # Save or update the user's Spotify profile
    spotify_profile, created = SpotifyProfile.objects.update_or_create(
        user=request.user,
        defaults={
            'spotify_token': token_info['access_token'],
            'refresh_token': token_info['refresh_token'],
            'token_expires': timezone.now() + timezone.timedelta(seconds=token_info['expires_in'])
        }
    )

    return redirect('home')

@login_required
def home_view(request):
    try:
        spotify_profile = request.user.spotifyprofile
        is_connected = True
    except SpotifyProfile.DoesNotExist:
        is_connected = False

    return render(request, 'home/home.html', {
        'username': request.user.username,
        'is_connected': is_connected
    })