from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="accounts:login", permanent=False)),
    path("", include("apps.accounts.urls")),
    path("", include("apps.routesheets.urls")),
    path("", include("apps.directory.urls")),
    path("panel/", include("apps.panel.urls")),
]
