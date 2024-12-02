from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
]

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('accounts.urls')),
    path('', include('home.urls')),
    path('', include('spotify.urls')),
    path('', include('navigation.urls')),
    path('en/RainbowMode/', include('spotify.urls')), 
        path('spotify/', include('spotify.urls')),

)
