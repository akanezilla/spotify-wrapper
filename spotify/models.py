from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from spotipy.oauth2 import SpotifyOAuth
from django.conf import settings

class SpotifyProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    spotify_token = models.TextField()
    refresh_token = models.TextField()
    token_expires = models.DateTimeField()

    def __str__(self):
        return f"{self.user.username}'s Spotify Profile"

    def refresh_spotify_token(self):
        sp_oauth = SpotifyOAuth(
            client_id=settings.SPOTIFY_CLIENT_ID,
            client_secret=settings.SPOTIFY_CLIENT_SECRET,
            redirect_uri=settings.SPOTIFY_REDIRECT_URI,
            scope="user-read-email user-top-read user-read-recently-played"
        )
        token_info = sp_oauth.refresh_access_token(self.refresh_token)

        self.spotify_token = token_info['access_token']
        self.token_expires = timezone.now() + timezone.timedelta(seconds=token_info['expires_in'])
        self.save()
