
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.views import View
from django.contrib.auth import logout
from django.shortcuts import redirect
import logging
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import render
from spotify.models import SpotifyProfile
from django.utils.translation import gettext_lazy as _

@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, 'Your account has been deleted.')
        return redirect('home')
    return render(request, 'delete_account.html')

logger = logging.getLogger(__name__)

class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            self.object = form.save()
            print("User created successfully. Redirecting to:", self.success_url)
            return HttpResponseRedirect(self.success_url)
        else:
            print("Form invalid. Errors:", form.errors)
            return self.form_invalid(form)

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


def contact_view(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        # Compose the email
        subject = f"New Contact Form Submission from {name}"
        body = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"

        try:
            # Send the email
            send_mail(
                subject,
                body,
                email,  # From email (user's email)
                ['jadelee1721l@gmail.com'],  # Replace with your receiving email
                fail_silently=False,
            )
            return JsonResponse({'success': True, 'message': 'Email sent successfully!'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return render(request, 'home/contact.html')  # Replace with your template name