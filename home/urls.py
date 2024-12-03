from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),  # Home page URL
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact, name='contact'),
    path('new-wrapped/', views.new_wrapped, name='new_wrapped'),
    path('past-wraps/', views.past_wraps, name='past_wraps'),
    path('account/', views.account, name='account'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
]
