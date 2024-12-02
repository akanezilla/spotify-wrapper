from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from spotify.models import SpotifyProfile
from django.contrib.auth import logout
from django.shortcuts import redirect

@login_required
def home_view(request):
    try:
        spotify_profile = SpotifyProfile.objects.get(user=request.user)
        is_connected = spotify_profile.spotify_token is not None
    except SpotifyProfile.DoesNotExist:
        is_connected = False

    return render(request, 'home/home.html', {
        'username': request.user.username,
        'is_connected': is_connected
    })

@login_required
def about_view(request):
    return render(request, 'home/about.html')

@login_required
def contact(request):
    return render(request, 'home/contact.html')

@login_required
def new_wrapped(request):
    return render(request, 'home/new-wrapped.html')

@login_required
def past_wraps(request):
    return render(request, 'home/past-wraps.html')

@login_required
def account(request):
    return render(request, 'home/account.html')

def login_view(request):
    return render(request, 'registration/login.html')

def signup_view(request):
    return render(request, 'registration/signup.html')

