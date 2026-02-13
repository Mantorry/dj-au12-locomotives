from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden

class RoleRequiredMixin(LoginRequiredMixin):
    allowed_roles: set[str] = set()

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)

        if getattr(request.user, "is_superuser", False):
            return super().dispatch(request, *args, **kwargs)

        if self.allowed_roles and getattr(request.user, "role", None) not in self.allowed_roles:
            return HttpResponseForbidden("Недостаточно прав.")
        return super().dispatch(request, *args, **kwargs)
