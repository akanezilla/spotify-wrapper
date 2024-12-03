from django.urls import path
from .views import SignUpView, CustomLoginView, delete_account, logout_view, contact_view
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),
    path("signup/", SignUpView.as_view(), name="signup"),
    path('logout/', logout_view, name='logout'),  # Use your custom logout view
    path('delete-account/', delete_account, name='delete_account'),
    path('contact/', contact_view, name='contact'),
]
