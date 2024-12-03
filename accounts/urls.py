from django.urls import path

from home.views import signup_view
from .views import CustomLoginView, delete_account, logout_view, contact_view
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),
    path("signup/", signup_view, name="signup"),
    path('logout/', logout_view, name='logout'),  # Use your custom logout view
    path('delete-account/', delete_account, name='delete_account'),
    path('contact/', contact_view, name='contact'),
]
