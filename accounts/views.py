
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.views import View
from django.contrib.auth import logout
from django.shortcuts import redirect
from spotify.models import SpotifyProfile
from django.contrib.auth.models import User

# Signup View
def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Validate passwords
        if password1 != password2:
            messages.error(request, "Passwords do not match!")
            return redirect('signup')

        # Check for existing username
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect('signup')

        # Create new user
        User.objects.create_user(username=username, password=password1)
        messages.success(request, "Account created successfully! Please log in.")
        return redirect('login')

    return render(request, 'registration/signup.html')


# Login View
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            print("Login successful for:", username)
            return redirect('home')  # Replace with your homepage URL name
        else:
            messages.error(request, "Invalid username or password!")
            print("Redirecting to login due to invalid credentials")
            return redirect('login')

    return render(request, 'registration/login.html')


@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, 'Your account has been deleted.')
        return redirect('home')
    return render(request, 'delete_account.html')

@login_required
def logout_view(request):
    # Clear Spotify profile if it exists
    if hasattr(request.user, 'spotifyprofile'):
        request.user.spotifyprofile.delete()

    # Clear any Spotify-related session data
    keys_to_remove = [key for key in request.session.keys() if 'spotify' in key.lower()]
    for key in keys_to_remove:
        del request.session[key]

    logout(request)
    return redirect('home')
