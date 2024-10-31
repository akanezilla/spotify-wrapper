from django.urls import path
from django.contrib.auth import views as auth_views
from .views import SignUpView, CustomLoginView
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),
    path("signup/", SignUpView.as_view(), name="signup"),
    path('logout/', LogoutView.as_view(), name='logout'),

]
