from django.urls import path
from .views import HomeView

app_name = "directory"

urlpatterns = [
    path("directory/", HomeView.as_view(), name="home"),
]