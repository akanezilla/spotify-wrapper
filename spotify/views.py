from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from spotipy.oauth2 import SpotifyOAuth
from django.conf import settings
from .models import SpotifyProfile
from django.utils import timezone
import secrets

@login_required
def spotify_connect(request):
     # Clear any existing Spotify profile for this user
    SpotifyProfile.objects.filter(user=request.user).delete()
    
    # Clear any Spotify-related session data
    keys_to_remove = [key for key in request.session.keys() if 'spotify' in key.lower()]
    for key in keys_to_remove:
        del request.session[key]
    
    # Generate a unique state for this request
    state = secrets.token_urlsafe(16)
    request.session['spotify_auth_state'] = state

    # Clear any existing Spotify profile for this user
    SpotifyProfile.objects.filter(user=request.user).delete()

    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI,
        state=state,
        scope="user-read-private user-read-email user-top-read user-read-recently-played"
    )
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@login_required
def spotify_callback(request):
    # Verify the state
    stored_state = request.session.pop('spotify_auth_state', None)
    state = request.GET.get('state')
    
    if state is None or state != stored_state:
        messages.error(request, "State verification failed.")
        return redirect('home')

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
        spotify_profile = SpotifyProfile.objects.get(user=request.user)
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