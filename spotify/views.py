from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from spotipy.oauth2 import SpotifyOAuth
from django.conf import settings
from .models import SpotifyProfile
from django.utils import timezone
import secrets
import spotipy
from spotipy.exceptions import SpotifyException
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import SpotifyProfile
import random


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
            # Get top tracks
            top_tracks = sp.current_user_top_tracks(limit=5, time_range='short_term')
            
            # Get top artists
            top_artists = sp.current_user_top_artists(limit=5, time_range='short_term')
            
            # Get recently played tracks to determine listener type
            recent_tracks = sp.current_user_recently_played(limit=50)
            
            # Analyze genres
            genres = {}
            for artist in top_artists['items']:
                for genre in artist['genres']:
                    genres[genre] = genres.get(genre, 0) + 1
            top_genre = max(genres, key=genres.get) if genres else "Unknown"
            
            # Determine listener type
            unique_artists = len(set([track['track']['artists'][0]['id'] for track in recent_tracks['items']]))
            if unique_artists > 30:
                listener_type = "Explorer"
            elif unique_artists > 15:
                listener_type = "Diverse"
            else:
                listener_type = "Focused"

            # Get total listening time
            total_duration_ms = sum(track['track']['duration_ms'] for track in recent_tracks['items'])
            total_duration_minutes = total_duration_ms / (1000 * 60)  # Convert to minutes

            # Get random songs
            random_tracks = random.sample(top_tracks['items'], min(3, len(top_tracks['items'])))
            
            # Prepare context
            context = {
                'top_song': top_tracks['items'][0] if top_tracks['items'] else None,
                'top_5_tracks': top_tracks['items'][:5],
                'top_artists': [artist['name'] for artist in top_artists['items']],
                'top_genre': top_genre,
                'listener_type': listener_type,
                'total_duration': total_duration_minutes,
                'random_tracks': random_tracks,
            }
            
            return render(request, 'spotify/spotify_data.html', context)
        except SpotifyException as e:
            messages.error(request, f"Spotify API error: {str(e)}")
            return redirect('home')
        
    except SpotifyProfile.DoesNotExist:
        messages.warning(request, "Please connect your Spotify account first.")
        return redirect('spotify_connect')
@login_required
def top_tracks_view(request):
    try:
        spotify_profile = request.user.spotifyprofile
        
        if spotify_profile.token_expires <= timezone.now():
            spotify_profile.refresh_spotify_token()
        
        sp = spotipy.Spotify(auth=spotify_profile.spotify_token)
        
        top_tracks = sp.current_user_top_tracks(limit=5, time_range='short_term')
        
        context = {
            'top_tracks': top_tracks['items']
        }
        return render(request, 'spotify/top_tracks.html', context)
    except SpotifyProfile.DoesNotExist:
        messages.warning(request, "Please connect your Spotify account first.")
        return redirect('spotify:spotify_connect')
    except SpotifyException as e:
        messages.error(request, f"Spotify API error: {str(e)}")
        return redirect('home')

@login_required
def top_artists_view(request):
    try:
        spotify_profile = request.user.spotifyprofile
        
        if spotify_profile.token_expires <= timezone.now():
            spotify_profile.refresh_spotify_token()
        
        sp = spotipy.Spotify(auth=spotify_profile.spotify_token)
        
        top_artists = sp.current_user_top_artists(limit=5, time_range='short_term')
        
        context = {
            'top_artists': top_artists['items']
        }
        return render(request, 'spotify/top_artists.html', context)
    except SpotifyProfile.DoesNotExist:
        messages.warning(request, "Please connect your Spotify account first.")
        return redirect('spotify:spotify_connect')
    except SpotifyException as e:
        messages.error(request, f"Spotify API error: {str(e)}")
        return redirect('home')

@login_required
def top_genre_view(request):
    try:
        spotify_profile = request.user.spotifyprofile
        
        if spotify_profile.token_expires <= timezone.now():
            spotify_profile.refresh_spotify_token()
        
        sp = spotipy.Spotify(auth=spotify_profile.spotify_token)
        
        top_artists = sp.current_user_top_artists(limit=50, time_range='medium_term')
        
        genres = {}
        for artist in top_artists['items']:
            for genre in artist['genres']:
                genres[genre] = genres.get(genre, 0) + 1
        
        top_genres = sorted(genres.items(), key=lambda x: x[1], reverse=True)[:5]
        
        context = {
            'top_genres': top_genres
        }
        return render(request, 'spotify/top_genre.html', context)
    except SpotifyProfile.DoesNotExist:
        messages.warning(request, "Please connect your Spotify account first.")
        return redirect('spotify:spotify_connect')
    except SpotifyException as e:
        messages.error(request, f"Spotify API error: {str(e)}")
        return redirect('home')

@login_required
def listener_type_view(request):
    try:
        spotify_profile = request.user.spotifyprofile
        
        if spotify_profile.token_expires <= timezone.now():
            spotify_profile.refresh_spotify_token()
        
        sp = spotipy.Spotify(auth=spotify_profile.spotify_token)
        
        recent_tracks = sp.current_user_recently_played(limit=50)
        
        unique_artists = len(set([track['track']['artists'][0]['id'] for track in recent_tracks['items']]))
        if unique_artists > 30:
            listener_type = "Explorer"
        elif unique_artists > 15:
            listener_type = "Diverse"
        else:
            listener_type = "Focused"
        
        context = {
            'listener_type': listener_type,
            'unique_artists': unique_artists
        }
        return render(request, 'spotify/listener_type.html', context)
    except SpotifyProfile.DoesNotExist:
        messages.warning(request, "Please connect your Spotify account first.")
        return redirect('spotify:spotify_connect')
    except SpotifyException as e:
        messages.error(request, f"Spotify API error: {str(e)}")
        return redirect('home')
@login_required
def random_songs_view(request):
    try:
        spotify_profile = request.user.spotifyprofile
        
        if spotify_profile.token_expires <= timezone.now():
            spotify_profile.refresh_spotify_token()
        
        sp = spotipy.Spotify(auth=spotify_profile.spotify_token)
        
        # Get top tracks
        top_tracks = sp.current_user_top_tracks(limit=50, time_range='short_term')
        
        # Select 3 random tracks
        random_tracks = random.sample(top_tracks['items'], min(3, len(top_tracks['items'])))
        
        context = {
            'random_tracks': random_tracks
        }
        return render(request, 'spotify/random_songs.html', context)
    except SpotifyProfile.DoesNotExist:
        messages.warning(request, "Please connect your Spotify account first.")
        return redirect('spotify:spotify_connect')
    except SpotifyException as e:
        messages.error(request, f"Spotify API error: {str(e)}")
        return redirect('home')
@login_required
def total_listening_time_view(request):
    try:
        spotify_profile = request.user.spotifyprofile
        
        if spotify_profile.token_expires <= timezone.now():
            spotify_profile.refresh_spotify_token()
        
        sp = spotipy.Spotify(auth=spotify_profile.spotify_token)
        
        # Get recently played tracks
        recent_tracks = sp.current_user_recently_played(limit=50)
        
        total_duration = sum(track['track']['duration_ms'] for track in recent_tracks['items'])
        total_duration_minutes = total_duration / (1000 * 60)  # Convert to minutes
        
        context = {
            'total_duration': total_duration_minutes
        }
        return render(request, 'spotify/total_listening_time.html', context)
    except SpotifyProfile.DoesNotExist:
        messages.warning(request, "Please connect your Spotify account first.")
        return redirect('spotify:spotify_connect')
    except SpotifyException as e:
        messages.error(request, f"Spotify API error: {str(e)}")
        return redirect('home')
@login_required
def top_song_view(request):
    try:
        spotify_profile = request.user.spotifyprofile
        
        if spotify_profile.token_expires <= timezone.now():
            spotify_profile.refresh_spotify_token()
        
        sp = spotipy.Spotify(auth=spotify_profile.spotify_token)
        
        # Get top tracks
        top_tracks = sp.current_user_top_tracks(limit=1, time_range='short_term')
        
        context = {
            'top_song': top_tracks['items'][0] if top_tracks['items'] else None
        }
        return render(request, 'spotify/top_song.html', context)
    except SpotifyProfile.DoesNotExist:
        messages.warning(request, "Please connect your Spotify account first.")
        return redirect('spotify:spotify_connect')
    except SpotifyException as e:
        messages.error(request, f"Spotify API error: {str(e)}")
        return redirect('home')
@login_required
def listening_trends_view(request):
    try:
        spotify_profile = request.user.spotifyprofile
        
        if spotify_profile.token_expires <= timezone.now():
            spotify_profile.refresh_spotify_token()
        
        sp = spotipy.Spotify(auth=spotify_profile.spotify_token)
        
        # Get recently played tracks
        recent_tracks = sp.current_user_recently_played(limit=100)  # Fetch more data if needed
        
        monthly_data = {}
        
        for track in recent_tracks['items']:
            played_at = track['played_at']
            month_year = played_at[:7]  # Extract YYYY-MM
            
            track_name = track['track']['name']
            artist_name = track['track']['artists'][0]['name']
            
            if month_year not in monthly_data:
                monthly_data[month_year] = []
            
            monthly_data[month_year].append(f"{track_name} by {artist_name}")
        
        context = {
            'monthly_data': monthly_data
        }
        
        return render(request, 'spotify/listening_trends.html', context)
    except SpotifyProfile.DoesNotExist:
        messages.warning(request, "Please connect your Spotify account first.")
        return redirect('spotify:spotify_connect')
    except SpotifyException as e:
        messages.error(request, f"Spotify API error: {str(e)}")
        return redirect('home')
@login_required
def color_inspired_playlist_view(request):
    try:
        spotify_profile = request.user.spotifyprofile
        
        if spotify_profile.token_expires <= timezone.now():
            spotify_profile.refresh_spotify_token()
        
        sp = spotipy.Spotify(auth=spotify_profile.spotify_token)
        
        if request.method == 'POST':
            color = request.POST.get('color', '').lower()
            
            # Define color-related keywords
            color_keywords = {
                'blue': ['cool', 'calm', 'melancholy', 'ocean', 'sky'],
                'red': ['passion', 'energy', 'anger', 'love', 'fire'],
                'green': ['nature', 'growth', 'fresh', 'harmony', 'balance'],
                'yellow': ['happy', 'sunny', 'cheerful', 'bright', 'optimistic'],
                'purple': ['royal', 'mysterious', 'creative', 'spiritual', 'luxurious'],
                'orange': ['warm', 'energetic', 'autumn', 'sunset', 'vibrant'],
                'pink': ['romantic', 'gentle', 'sweet', 'feminine', 'soft'],
                'gold': ['luxury', 'success', 'achievement', 'wealth', 'prestige'],
                'silver': ['modern', 'sleek', 'futuristic', 'cool', 'sophisticated'],
                'brown': ['earthy', 'natural', 'rustic', 'warm', 'cozy']
            }
            
            keywords = color_keywords.get(color, [color])
            
            # Search for tracks based on color keywords
            tracks = []
            for keyword in keywords:
                results = sp.search(q=keyword, type='track', limit=5)
                tracks.extend(results['tracks']['items'])
            
            # Create a new playlist
            user_id = sp.me()['id']
            playlist_name = f"{color.capitalize()} Inspired Playlist"
            playlist = sp.user_playlist_create(user_id, playlist_name, public=False)
            
            # Add tracks to the playlist
            track_uris = [track['uri'] for track in tracks[:20]]  # Limit to 20 tracks
            sp.user_playlist_add_tracks(user_id, playlist['id'], track_uris)
            
            context = {
                'playlist_url': playlist['external_urls']['spotify'],
                'color': color,
                'tracks': tracks[:20]
            }
            return render(request, 'spotify/color_playlist_result.html', context)
        
        return render(request, 'spotify/color_playlist_form.html')
    
    except SpotifyProfile.DoesNotExist:
        messages.warning(request, "Please connect your Spotify account first.")
        return redirect('spotify:spotify_connect')
    except SpotifyException as e:
        messages.error(request, f"Spotify API error: {str(e)}")
        return redirect('home')