from django import forms
from .models import SavedWrap

class WrapForm(forms.ModelForm):
    class Meta:
        model = SavedWrap
        fields = [
            'listening_minutes', 
            'memorable_moments', 
            'top_5_songs', 
            'top_5_artists', 
            'top_5_genres', 
            'top_song', 
            'type_of_listener',
        ]
