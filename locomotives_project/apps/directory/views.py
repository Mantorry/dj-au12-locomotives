from django.views.generic import TemplateView
from apps.accounts.permissions import RoleRequiredMixin
from apps.accounts.models import Role

class HomeView(RoleRequiredMixin, TemplateView):
    allowed_roles = {Role.ADMIN, Role.MASTER, Role.MACHINIST, Role.ASSISTANT, Role.MEDIC, Role.INSPECTOR}
    template_name = "directory/home.html"