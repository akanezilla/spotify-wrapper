from django.http import JsonResponse
from spotipy.oauth2 import SpotifyOAuth
from django.conf import settings
import secrets
import spotipy
from spotipy.exceptions import SpotifyException
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import SpotifyProfile
import random
from django.utils.translation import gettext as _
from django.utils.timezone import now
import logging
from collections import Counter
from spotipy import Spotify



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

        # Fetch user's top tracks
        top_tracks = sp.current_user_top_tracks(limit=5, time_range='long_term')

        # Extract relevant information including cover photo URL
        tracks_info = []
        for track in top_tracks['items']:
            cover_url = track['album']['images'][0]['url'] if track['album']['images'] else '/static/images/default_cover.jpg'
            tracks_info.append({
                'name': track['name'],
                'artist': track['artists'][0]['name'],
                'cover_url': cover_url,
                'id': track['id']  # Store the track ID if needed
            })

        context = {
            'top_tracks': tracks_info
        }
        return render(request, 'RainbowMode/top_5_songs.html', context)

    except SpotifyProfile.DoesNotExist:
        messages.warning(request, "Please connect your Spotify account first.")
        return redirect('spotify:spotify_connect')
    except SpotifyException as e:
        messages.error(request, f"Spotify API error: {str(e)}")
        return redirect('home')
    
@login_required
def top_artists_rb(request):
    try:
        spotify_profile = request.user.spotifyprofile

        # Check if the Spotify token is expired and refresh if necessary
        if spotify_profile.token_expires <= timezone.now():
            spotify_profile.refresh_spotify_token()

        sp = spotipy.Spotify(auth=spotify_profile.spotify_token)

        # Get top 5 artists from Spotify
        top_artists = sp.current_user_top_artists(limit=5, time_range='long_term')

        # Prepare artist data for template
        artists_info = [{
            'name': artist['name'],
            'image_url': artist['images'][0]['url'] if artist['images'] else '/static/images/default_artist.jpg',  # Default image if none available
            'genres': ', '.join(artist['genres'][:3])  # Limit to top 3 genres
        } for artist in top_artists['items']]

        context = {
            'top_artists': artists_info,
            'card_images': [
                'StarCardRB.svg',
                'swordCardRB.svg',
                'SunCardRB.svg',
                'moonCardRB.svg',
                'heartCardRB.svg'
            ],
        }
        return render(request, 'RainbowMode/top_artists.html', context)

    except SpotifyProfile.DoesNotExist:
        messages.warning(request, "Please connect your Spotify account first.")
        return redirect('spotify:spotify_connect')
    except Exception as e:
        messages.error(request, f"Spotify API error: {str(e)}")
        return redirect('home')


def top_genre_view(request):
    try:
        spotify_profile = request.user.spotifyprofile

        if spotify_profile.token_expires <= timezone.now():
            spotify_profile.refresh_spotify_token()

        sp = spotipy.Spotify(auth=spotify_profile.spotify_token)

        top_artists = sp.current_user_top_artists(limit=50, time_range="medium_term")
        genres = {}

        for artist in top_artists['items']:
            for genre in artist['genres']:
                genres[genre] = genres.get(genre, 0) + 1

        sorted_genres = sorted(genres.items(), key=lambda x: x[1], reverse=True)
        top_genres = sorted_genres[:5]

        # Calculate percentages
        total_count = sum(count for _, count in top_genres)
        top_genres_with_percentage = [
            (genre, count, (count / total_count) * 100)
            for genre, count in top_genres
        ]

        return JsonResponse({"top_genres": top_genres_with_percentage})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@login_required
def listener_type_view(request):
    try:
        spotify_profile = request.user.spotifyprofile

        if spotify_profile.token_expires <= timezone.now():
            spotify_profile.refresh_spotify_token()

        sp = spotipy.Spotify(auth=spotify_profile.spotify_token)

        # Get top tracks and artists for the long term (approximately last year)
        top_tracks = sp.current_user_top_tracks(limit=50, time_range='long_term')
        top_artists = sp.current_user_top_artists(limit=50, time_range='long_term')

        # Count unique artists from top tracks
        track_artists = [track['artists'][0]['id'] for track in top_tracks['items']]

        # Add artists from top artists
        artist_ids = [artist['id'] for artist in top_artists['items']]

        # Combine and count unique artists
        all_artists = track_artists + artist_ids
        unique_artists = len(set(all_artists))

        # Count repetitions
        artist_counts = Counter(all_artists)
        repeat_listens = sum(count for count in artist_counts.values() if count > 1)

        # Determine listener type
        if unique_artists > 40:
            listener_type = "Explorer"
        elif unique_artists > 25:
            listener_type = "Diverse"
        else:
            listener_type = "Focused"

        # Additional context
        total_artists = len(all_artists)
        diversity_score = (unique_artists / total_artists) * 100

        context = {
            'listener_type': listener_type,
            'unique_artists': unique_artists,
            'total_artists': total_artists,
            'diversity_score': round(diversity_score, 2),
            'repeat_listens': repeat_listens
        }
        return render(request, 'RainbowMode/type_of_listener.html', context)
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

        # Select 3 random tracks and extract relevant information
        random_tracks = random.sample(top_tracks['items'], min(3, len(top_tracks['items'])))
        track_info = []
        for track in random_tracks:
            track_info.append({
                'name': track['name'],
                'artist': track['artists'][0]['name'],
                'cover_url': track['album']['images'][0]['url'] if track['album']['images'] else None
            })

        context = {
            'random_tracks': track_info
        }
        return render(request, 'spotify/random_songs.html', context)
    except SpotifyProfile.DoesNotExist:
        messages.warning(request, "Please connect your Spotify account first.")
        return redirect('spotify:spotify_connect')
    except SpotifyException as e:
        messages.error(request, f"Spotify API error: {str(e)}")
        return redirect('home')


from django.http import JsonResponse


@login_required
def total_listening_time_view(request):
    try:
        # Ensure the user has a Spotify profile
        spotify_profile = request.user.spotifyprofile

        # Refresh token if expired
        if spotify_profile.token_expires <= now():
            spotify_profile.refresh_spotify_token()

        # Connect to Spotify API
        sp = spotipy.Spotify(auth=spotify_profile.spotify_token)

        # Fetch top tracks and calculate total listening time
        top_tracks = sp.current_user_top_tracks(limit=50, time_range='long_term')
        total_duration = sum(track['duration_ms'] for track in top_tracks['items'])
        total_duration_minutes = round(total_duration / (1000 * 60))  # Convert ms to minutes

        # Estimate yearly listening time
        estimated_yearly_minutes = total_duration_minutes * 20  # Adjust multiplier as needed

        # Return JSON response
        return JsonResponse({'listening_minutes': estimated_yearly_minutes})

    except SpotifyProfile.DoesNotExist:
        return JsonResponse({'error': 'Spotify account not connected'}, status=400)

    except SpotifyException as e:
        return JsonResponse({'error': f'Spotify API error: {str(e)}'}, status=500)

    except Exception as e:
        return JsonResponse({'error': f'Unexpected error: {str(e)}'}, status=500)


@login_required
def top_song_view(request):
    try:
        spotify_profile = request.user.spotifyprofile

        if spotify_profile.token_expires <= timezone.now():
            spotify_profile.refresh_spotify_token()

        sp = spotipy.Spotify(auth=spotify_profile.spotify_token)

        top_tracks = sp.current_user_top_tracks(limit=1, time_range='long_term')

        if top_tracks['items']:
            top_song = top_tracks['items'][0]
            data = {
                'top_song': {
                    'name': top_song['name'],
                    'artist': top_song['artists'][0]['name'],
                    'cover_url': top_song['album']['images'][0]['url'] if top_song['album']['images'] else None,
                    'preview_url': top_song['preview_url'],
                    'spotify_url': top_song['external_urls']['spotify']
                }
            }
        else:
            data = {'top_song': None}

        return JsonResponse(data)
    except SpotifyProfile.DoesNotExist:
        return JsonResponse({'error': 'Please connect your Spotify account first.'}, status=400)
    except SpotifyException as e:
        return JsonResponse({'error': f'Spotify API error: {str(e)}'}, status=500)

@login_required
def spotify_wrapped_view(request):
    try:
        spotify_profile = request.user.spotifyprofile
        if spotify_profile.token_expires <= timezone.now():
            spotify_profile.refresh_spotify_token()

        sp = spotipy.Spotify(auth=spotify_profile.spotify_token)

        # Fetch all required data
        top_tracks = sp.current_user_top_tracks(limit=5, time_range='short_term')['items']
        top_artists = sp.current_user_top_artists(limit=5, time_range='short_term')['items']

        # Top genres
        all_artists = sp.current_user_top_artists(limit=50, time_range='medium_term')['items']
        genres = {}
        for artist in all_artists:
            for genre in artist['genres']:
                genres[genre] = genres.get(genre, 0) + 1
        top_genres = sorted(genres.items(), key=lambda x: x[1], reverse=True)[:5]

        # Listener type
        recent_tracks = sp.current_user_recently_played(limit=50)['items']
        unique_artists = len(set([track['track']['artists'][0]['id'] for track in recent_tracks]))
        if unique_artists > 30:
            listener_type = "Explorer"
        elif unique_artists > 15:
            listener_type = "Diverse"
        else:
            listener_type = "Focused"

        # Random songs
        random_tracks = random.sample(top_tracks, min(3, len(top_tracks)))

        # Total listening time
        total_duration = sum(track['track']['duration_ms'] for track in recent_tracks)
        total_duration_minutes = total_duration / (1000 * 60)

        # Top song
        top_song = top_tracks[0] if top_tracks else None

        # Memorable moment
        all_tracks = top_tracks + recent_tracks
        memorable_track = random.choice(all_tracks)
        artist_info = sp.artist(memorable_track['track']['artists'][0]['id'])
        moment_description = generate_moment_description(memorable_track['track'], artist_info)

        context = {
            'top_tracks': top_tracks,
            'top_artists': top_artists,
            'top_genres': top_genres,
            'listener_type': listener_type,
            'unique_artists': unique_artists,
            'random_tracks': random_tracks,
            'total_duration_minutes': total_duration_minutes,
            'top_song': top_song,
            'memorable_track': memorable_track['track'],
            'moment_description': moment_description,
        }

        return render(request, 'spotify/wrapped.html', context)
    except SpotifyProfile.DoesNotExist:
        messages.warning(request, "Please connect your Spotify account first.")
        return redirect('spotify:spotify_connect')
    except SpotifyException as e:
        messages.error(request, f"Spotify API error: {str(e)}")
        return redirect('home')


@login_required
def memorable_moment_view(request):
    try:
        spotify_profile = request.user.spotifyprofile

        if spotify_profile.token_expires <= timezone.now():
            spotify_profile.refresh_spotify_token()

        sp = spotipy.Spotify(auth=spotify_profile.spotify_token)

        # Get top tracks of the year
        top_tracks = sp.current_user_top_tracks(limit=50, time_range='long_term')

        # Get recently played tracks
        recent_tracks = sp.current_user_recently_played(limit=50)

        # Combine and shuffle the tracks
        all_tracks = top_tracks['items'] + recent_tracks['items']
        random.shuffle(all_tracks)

        # Select a random track as the "memorable moment"
        memorable_track = random.choice(all_tracks)

        # Get additional context for the track
        track_info = sp.track(memorable_track['id'])
        artist_info = sp.artist(track_info['artists'][0]['id'])

        data = {
            'track_name': track_info['name'],
            'artist_name': artist_info['name'],
            'track_image': track_info['album']['images'][0]['url'],
            'moment_description': generate_moment_description(track_info, artist_info)
        }

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse(data)

        return render(request, 'spotify/memorable_moment.html', {'initial_data': json.dumps(data)})

    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': str(e)}, status=400)
        messages.error(request, str(e))
        return redirect('home')


def generate_moment_description(track, artist):
    """Generate a description for the memorable moment."""
    moments = [
        f"Remember when you couldn't stop playing '{track['name']}' by {artist['name']}?",
        f"That time '{track['name']}' became the soundtrack to your life.",
        f"When {artist['name']}'s '{track['name']}' hit differently and became your anthem.",
        f"The day you discovered '{track['name']}' and fell in love with {artist['name']}'s music.",
        f"That perfect moment when '{track['name']}' came on and everything felt right."
    ]
    return random.choice(moments)
@login_required
def top_5_songs_rb(request):
    try:
        spotify_profile = request.user.spotifyprofile

        if spotify_profile.token_expires <= timezone.now():
            spotify_profile.refresh_spotify_token()

        sp = spotipy.Spotify(auth=spotify_profile.spotify_token)

        # Fetch user's top tracks
        top_tracks = sp.current_user_top_tracks(limit=5, time_range='long_term')
        tracks_info = []
        for track in top_tracks['items']:
            cover_url = track['album']['images'][0]['url'] if track['album']['images'] else '/static/images/default_cover.jpg'
            tracks_info.append({
                'name': track['name'],
                'artist': track['artists'][0]['name'],
                'cover_url': cover_url,
                'id': track['id']
            })

        # Example card images list
        card_images = [
            'StarCardRB.svg',
            'swordCardRB.svg',
            'SunCardRB.svg',
            'moonCardRB.svg',
            'heartCardRB.svg'
        ]

        context = {
            'top_tracks': tracks_info,
            'card_images': card_images,
        }
        return render(request, 'RainbowMode/top_5_songs.html', context)

    except SpotifyProfile.DoesNotExist:
        messages.warning(request, "Please connect your Spotify account first.")
        return redirect('spotify:spotify_connect')
    except SpotifyException as e:
        messages.error(request, f"Spotify API error: {str(e)}")
        return redirect('home')