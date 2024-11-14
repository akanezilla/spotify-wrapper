from django.shortcuts import render, redirect

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.views import View
from django.contrib.auth import logout
from django.shortcuts import redirect
from spotify.models import SpotifyProfile

@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, 'Your account has been deleted.')
        return redirect('home')
    return render(request, 'delete_account.html')

class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"

class CustomLoginView(View):
    form_class = AuthenticationForm
    template_name = 'registration/login.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Use the name of your home URL pattern
        return render(request, self.template_name, {'form': form})

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