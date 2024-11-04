from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from spotipy.oauth2 import SpotifyOAuth
from django.conf import settings
from .models import SpotifyProfile
from django.utils import timezone

from django.shortcuts import redirect
from django.conf import settings
import urllib.parse

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from spotipy.oauth2 import SpotifyOAuth
from django.conf import settings
from .models import SpotifyProfile
from django.utils import timezone

from django.shortcuts import redirect
from django.conf import settings
import urllib.parse

from .models import SpotifyProfile
from django.utils import timezone
import requests
from django.contrib import messages


def spotify_connect(request):
    client_id = settings.SPOTIFY_CLIENT_ID
    redirect_uri = settings.SPOTIFY_REDIRECT_URI
    scope = 'user-read-private user-read-email user-top-read'

    params = {
        'client_id': client_id,
        'response_type': 'code',
        'redirect_uri': redirect_uri,
        'scope': scope,
    }

    auth_url = f"https://accounts.spotify.com/authorize?{urllib.parse.urlencode(params)}"
    return redirect(auth_url)
from .models import SpotifyProfile
from django.utils import timezone
import requests

@login_required
def spotify_callback(request):
    code = request.GET.get('code')
    
    if code:
        sp_oauth = SpotifyOAuth(
            client_id=settings.SPOTIFY_CLIENT_ID,
            client_secret=settings.SPOTIFY_CLIENT_SECRET,
            redirect_uri=settings.SPOTIFY_REDIRECT_URI,
            scope="user-read-email user-top-read user-read-recently-played"
        )
        
        token_info = sp_oauth.get_access_token(code)
        
        if token_info:
            access_token = token_info['access_token']
            refresh_token = token_info['refresh_token']
            expires_in = token_info['expires_in']
            
            # Update or create the SpotifyProfile for the user
            spotify_profile, created = SpotifyProfile.objects.update_or_create(
                user=request.user,
                defaults={
                    'spotify_token': access_token,
                    'refresh_token': refresh_token,
                    'token_expires': timezone.now() + timezone.timedelta(seconds=expires_in)
                }
            )
            
            return redirect('home')  # Redirect to your home page
        else:
            # Handle error case
            return redirect('home')
    else:
        # Handle error case
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
@login_required
def spotify_data_view(request):
    try:
        spotify_profile = request.user.spotifyprofile
        
        if spotify_profile.token_expires <= timezone.now():
            spotify_profile.refresh_spotify_token()
        
        sp = spotipy.Spotify(auth=spotify_profile.spotify_token)
        
        try:
            top_tracks = sp.current_user_top_tracks(limit=10, time_range='short_term')
            return render(request, 'spotify_data.html', {'top_tracks': top_tracks})
        except SpotifyException as e:
            messages.error(request, f"Spotify API error: {str(e)}")
            return redirect('home')
        
    except SpotifyProfile.DoesNotExist:
        messages.warning(request, "Please connect your Spotify account first.")
        return redirect('spotify_connect')


@login_required
def spotify_callback(request):
    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI,
        scope="user-read-private user-read-email user-top-read user-read-recently-played"
    )
    
    code = request.GET.get('code')
    
    if code:
        try:
            token_info = sp_oauth.get_access_token(code)
            
            if token_info:
                access_token = token_info['access_token']
                refresh_token = token_info['refresh_token']
                expires_in = token_info['expires_in']
                
                spotify_profile, created = SpotifyProfile.objects.update_or_create(
                    user=request.user,
                    defaults={
                        'spotify_token': access_token,
                        'refresh_token': refresh_token,
                        'token_expires': timezone.now() + timezone.timedelta(seconds=expires_in)
                    }
                )
                
                messages.success(request, "Successfully connected to Spotify!")
                return redirect('home')
            else:
                messages.error(request, "Failed to get token info from Spotify.")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
    else:
        messages.error(request, "No authorization code received from Spotify.")
    
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
@login_required
def spotify_data_view(request):
    try:
        spotify_profile = request.user.spotifyprofile
        
        # Check if token is expired and refresh if necessary
        if spotify_profile.token_expires <= timezone.now():
            spotify_profile.refresh_spotify_token()
        
        # Use the access token to make Spotify API calls
        sp = spotipy.Spotify(auth=spotify_profile.spotify_token)
        
        # Make your Spotify API calls here
        # For example:
        top_tracks = sp.current_user_top_tracks(limit=10, time_range='short_term')
        
        return render(request, 'spotify_data.html', {'top_tracks': top_tracks})
        
    except SpotifyProfile.DoesNotExist:
        # User hasn't connected to Spotify yet
        return redirect('spotify_connect')