from django.urls import path
from .views import AppLoginView, AppLogoutView, WorkerListView, RegisterUserView

app_name = "accounts"

urlpatterns = [
    path("login/", AppLoginView.as_view(), name="login"),
    path("logout/", AppLogoutView.as_view(), name="logout"),
    path("workers/", WorkerListView.as_view(), name="worker_list"),
    path("register/", RegisterUserView.as_view(), name="register"),
]