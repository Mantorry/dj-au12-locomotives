from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import get_user_model
from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from django.db.models import Q

from .permissions import RoleRequiredMixin
from .models import Role
from .forms import UserRegisterForm, WorkerFilterForm, _bootstrapify_form

User = get_user_model()

class AppLoginView(LoginView):
    template_name = "accounts/login.html"

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["username"].label = "Логин"
        form.fields["password"].label = "Пароль"
        _bootstrapify_form(form)
        return form

class AppLogoutView(LogoutView):
    pass

class RegisterUserView(RoleRequiredMixin, CreateView):
    allowed_roles = {Role.ADMIN}
    model = User
    form_class = UserRegisterForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("panel:user_list")

class WorkerListView(RoleRequiredMixin, ListView):
    allowed_roles = {Role.ADMIN, Role.MASTER, Role.INSPECTOR}
    model = User
    template_name = "accounts/worker_list.html"
    paginate_by = 50

    def get_queryset(self):
        qs = super().get_queryset().select_related("station").order_by("last_name", "first_name", "patronymic")
        role = self.request.GET.get("role") or ""
        q = self.request.GET.get("q") or ""
        if role:
            qs = qs.filter(role=role)
        if q:
            qs = qs.filter(
                Q(username__icontains=q) |
                Q(first_name__icontains=q) |
                Q(last_name__icontains=q) |
                Q(patronymic__icontains=q)
            )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["filter_form"] = WorkerFilterForm(self.request.GET)
        return ctx