from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import requests
from django.conf import settings

class SpotifyProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    spotify_token = models.TextField()
    refresh_token = models.TextField()
    token_expires = models.DateTimeField()

    def __str__(self):
        return f"{self.user.username}'s Spotify Profile"

    def refresh_spotify_token(self):
        # Spotify token refresh endpoint
        token_url = "https://accounts.spotify.com/api/token"

        # Prepare the request data
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "client_id": settings.SPOTIFY_CLIENT_ID,
            "client_secret": settings.SPOTIFY_CLIENT_SECRET,
        }

        # Make the POST request to refresh the token
        response = requests.post(token_url, data=data)

        if response.status_code == 200:
            refresh_data = response.json()
            self.spotify_token = refresh_data['access_token']
            self.token_expires = timezone.now() + timezone.timedelta(seconds=refresh_data['expires_in'])
            if 'refresh_token' in refresh_data:
                self.refresh_token = refresh_data['refresh_token']
            self.save()
        else:
            # Handle error - you might want to raise an exception or log this
            print(f"Error refreshing token: {response.status_code} - {response.text}")

        return self.spotify_token