from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def home_view(request):
    username = request.user.username if request.user.is_authenticated else "Guest"
    return render(request, 'home/home.html', {'username': username})
