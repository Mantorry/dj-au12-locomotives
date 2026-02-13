from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("", include("apps.accounts.urls")),
    path("", include("apps.routesheets.urls")),
    path("", include("apps.directory.urls")),
    path("panel/", include("apps.panel.urls")),
]
