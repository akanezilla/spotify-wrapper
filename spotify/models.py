from django.db import models
from django.contrib.auth.models import User

class SpotifyProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    spotify_token = models.TextField()
    refresh_token = models.TextField()
    token_expires = models.DateTimeField()

    def __str__(self):
        return f"{self.user.username}'s Spotify Profile"