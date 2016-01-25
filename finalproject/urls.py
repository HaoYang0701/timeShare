from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^guru/', include('guru.urls')),
    url(r'^$', 'guru.views.home'),
]
