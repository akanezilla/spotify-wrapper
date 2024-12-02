from django.urls import path
from .views import delete_account, logout_view, signup, login_view
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('signup/', signup, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),  # Use your custom logout view
    path('delete-account/', delete_account, name='delete_account'),
]