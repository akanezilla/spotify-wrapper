from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from spotipy.oauth2 import SpotifyOAuth
from .models import SpotifyProfile
from django.utils import timezone
from django.http import HttpResponse  # Add this import


@login_required
def spotify_connect(request):
    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI,
        scope="user-read-email user-top-read user-read-recently-played"
    )
    auth_url = sp_oauth.get_authorize_url()
    print(f"Redirecting to Spotify auth URL: {auth_url}")
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
    from django.shortcuts import redirect
    from django.contrib.auth.decorators import login_required
    from spotipy.oauth2 import SpotifyOAuth
    from django.conf import settings
    from .models import SpotifyProfile
    from django.utils import timezone
    from django.http import HttpResponse  # Add this import

    @login_required
    def spotify_connect(request):
        sp_oauth = SpotifyOAuth(
            client_id=settings.SPOTIFY_CLIENT_ID,
            client_secret=settings.SPOTIFY_CLIENT_SECRET,
            redirect_uri=settings.SPOTIFY_REDIRECT_URI,
            scope="user-read-email user-top-read user-read-recently-played"
        )
        auth_url = sp_oauth.get_authorize_url()
        print(f"Redirecting to Spotify auth URL: {auth_url}")  # Add this line for debugging
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

        if not code:
            return HttpResponse("No code provided")  # Add this line for debugging

        token_info = sp_oauth.get_access_token(code)

        if token_info:
            access_token = token_info['access_token']
            refresh_token = token_info['refresh_token']
            expires_in = token_info['expires_in']

            # Save or update the user's Spotify profile
            spotify_profile, created = SpotifyProfile.objects.update_or_create(
                user=request.user,
                defaults={
                    'spotify_token': access_token,
                    'refresh_token': refresh_token,
                    'token_expires': timezone.now() + timezone.timedelta(seconds=expires_in)
                }
            )

            # Redirect to a success page or home page
            return redirect('home')
        else:
            # Handle error - redirect to an error page or back to the home page
            return HttpResponse("Failed to get token info")  # Add this line for debugging
    if not code:
        return HttpResponse("No code provided")  # Add this line for debugging

    token_info = sp_oauth.get_access_token(code)

    if token_info:
        access_token = token_info['access_token']
        refresh_token = token_info['refresh_token']
        expires_in = token_info['expires_in']

        # Save or update the user's Spotify profile
        spotify_profile, created = SpotifyProfile.objects.update_or_create(
            user=request.user,
            defaults={
                'spotify_token': access_token,
                'refresh_token': refresh_token,
                'token_expires': timezone.now() + timezone.timedelta(seconds=expires_in)
            }
        )

        # Redirect to a success page or home page
        return redirect('home')
    else:
        # Handle error - redirect to an error page or back to the home page
        return HttpResponse("Failed to get token info")  # Add this line for debugging