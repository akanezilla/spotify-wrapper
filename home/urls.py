from django.urls import path
from .views import home_view, slideshow_view

urlpatterns = [
    path('', home_view, name='home'),  # This will make the home view available at the root of the app
    path('RainbowMode/transition1/', slideshow_view, name='slideshowRB'),
]
