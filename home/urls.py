from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),  # Home page URL
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact, name='contact'),
]
