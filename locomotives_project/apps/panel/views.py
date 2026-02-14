from django.views.generic import TemplateView, ListView, UpdateView, CreateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model

from apps.accounts.permissions import RoleRequiredMixin
from apps.accounts.models import Role
from apps.directory.models import Enterprise, Station, FuelType, LubricantType, SSPSUnit, Brigade
from apps.routesheets.models import RouteSheetAU12

from .forms import (
    UserEditForm,
    EnterpriseForm, StationForm, FuelTypeForm, LubricantTypeForm, SSPSUnitForm,
    BrigadeForm
)

User = get_user_model()

class PanelHomeView(RoleRequiredMixin, TemplateView):
    allowed_roles = {Role.ADMIN}
    template_name = "panel/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["cnt_users"] = User.objects.count()
        ctx["cnt_units"] = SSPSUnit.objects.count()
        ctx["cnt_rs"] = RouteSheetAU12.objects.count()
        ctx["cnt_brigades"] = Brigade.objects.count()
        return ctx

class PanelUserList(RoleRequiredMixin, ListView):
    allowed_roles = {Role.ADMIN}
    model = User
    template_name = "panel/user_list.html"
    paginate_by = 50

    def get_queryset(self):
        qs = super().get_queryset().select_related("station").order_by("last_name", "first_name", "patronymic")
        q = self.request.GET.get("q") or ""
        if q:
            from django.db.models import Q
            qs = qs.filter(
                Q(username__icontains=q) |
                Q(last_name__icontains=q) |
                Q(first_name__icontains=q) |
                Q(patronymic__icontains=q)
            )
        return qs

class PanelUserEdit(RoleRequiredMixin, UpdateView):
    allowed_roles = {Role.ADMIN}
    model = User
    form_class = UserEditForm
    template_name = "panel/form.html"
    success_url = reverse_lazy("panel:user_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "Редактировать пользователя"
        ctx["back_url"] = reverse_lazy("panel:user_list")
        return ctx

# Универсальные CRUD (по шаблону)
class EnterpriseList(RoleRequiredMixin, ListView):
    allowed_roles = {Role.ADMIN}
    model = Enterprise
    template_name = "panel/list.html"
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({"title":"Предприятия","create_url":reverse_lazy("panel:enterprise_create"),
                    "edit_name":"panel:enterprise_edit","delete_name":"panel:enterprise_delete"})
        return ctx

class EnterpriseCreate(RoleRequiredMixin, CreateView):
    allowed_roles = {Role.ADMIN}
    model = Enterprise
    form_class = EnterpriseForm
    template_name = "panel/form.html"
    success_url = reverse_lazy("panel:enterprise_list")
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"]="Добавить предприятие"; ctx["back_url"]=reverse_lazy("panel:enterprise_list")
        return ctx

class EnterpriseEdit(RoleRequiredMixin, UpdateView):
    allowed_roles = {Role.ADMIN}
    model = Enterprise
    form_class = EnterpriseForm
    template_name = "panel/form.html"
    success_url = reverse_lazy("panel:enterprise_list")
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"]="Редактировать предприятие"; ctx["back_url"]=reverse_lazy("panel:enterprise_list")
        return ctx

class EnterpriseDelete(RoleRequiredMixin, DeleteView):
    allowed_roles = {Role.ADMIN}
    model = Enterprise
    template_name = "panel/delete.html"
    success_url = reverse_lazy("panel:enterprise_list")
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"]="Удалить предприятие"; ctx["back_url"]=reverse_lazy("panel:enterprise_list")
        return ctx

class StationList(RoleRequiredMixin, ListView):
    allowed_roles = {Role.ADMIN}
    model = Station
    template_name = "panel/list.html"
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({"title":"Станции","create_url":reverse_lazy("panel:station_create"),
                    "edit_name":"panel:station_edit","delete_name":"panel:station_delete"})
        return ctx

class StationCreate(RoleRequiredMixin, CreateView):
    allowed_roles = {Role.ADMIN}
    model = Station
    form_class = StationForm
    template_name = "panel/form.html"
    success_url = reverse_lazy("panel:station_list")
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"]="Добавить станцию"; ctx["back_url"]=reverse_lazy("panel:station_list")
        return ctx

class StationEdit(RoleRequiredMixin, UpdateView):
    allowed_roles = {Role.ADMIN}
    model = Station
    form_class = StationForm
    template_name = "panel/form.html"
    success_url = reverse_lazy("panel:station_list")
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"]="Редактировать станцию"; ctx["back_url"]=reverse_lazy("panel:station_list")
        return ctx

class StationDelete(RoleRequiredMixin, DeleteView):
    allowed_roles = {Role.ADMIN}
    model = Station
    template_name = "panel/delete.html"
    success_url = reverse_lazy("panel:station_list")
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"]="Удалить станцию"; ctx["back_url"]=reverse_lazy("panel:station_list")
        return ctx

class FuelTypeList(RoleRequiredMixin, ListView):
    allowed_roles = {Role.ADMIN}
    model = FuelType
    template_name = "panel/list.html"
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({"title":"Топливо","create_url":reverse_lazy("panel:fuel_create"),
                    "edit_name":"panel:fuel_edit","delete_name":"panel:fuel_delete"})
        return ctx

class FuelTypeCreate(RoleRequiredMixin, CreateView):
    allowed_roles = {Role.ADMIN}
    model = FuelType
    form_class = FuelTypeForm
    template_name = "panel/form.html"
    success_url = reverse_lazy("panel:fuel_list")
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"]="Добавить топливо"; ctx["back_url"]=reverse_lazy("panel:fuel_list")
        return ctx

class FuelTypeEdit(RoleRequiredMixin, UpdateView):
    allowed_roles = {Role.ADMIN}
    model = FuelType
    form_class = FuelTypeForm
    template_name = "panel/form.html"
    success_url = reverse_lazy("panel:fuel_list")
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"]="Редактировать топливо"; ctx["back_url"]=reverse_lazy("panel:fuel_list")
        return ctx

class FuelTypeDelete(RoleRequiredMixin, DeleteView):
    allowed_roles = {Role.ADMIN}
    model = FuelType
    template_name = "panel/delete.html"
    success_url = reverse_lazy("panel:fuel_list")
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"]="Удалить топливо"; ctx["back_url"]=reverse_lazy("panel:fuel_list")
        return ctx

class LubricantTypeList(RoleRequiredMixin, ListView):
    allowed_roles = {Role.ADMIN}
    model = LubricantType
    template_name = "panel/list.html"
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({"title":"Смазки","create_url":reverse_lazy("panel:lube_create"),
                    "edit_name":"panel:lube_edit","delete_name":"panel:lube_delete"})
        return ctx

class LubricantTypeCreate(RoleRequiredMixin, CreateView):
    allowed_roles = {Role.ADMIN}
    model = LubricantType
    form_class = LubricantTypeForm
    template_name = "panel/form.html"
    success_url = reverse_lazy("panel:lube_list")
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"]="Добавить смазку"; ctx["back_url"]=reverse_lazy("panel:lube_list")
        return ctx

class LubricantTypeEdit(RoleRequiredMixin, UpdateView):
    allowed_roles = {Role.ADMIN}
    model = LubricantType
    form_class = LubricantTypeForm
    template_name = "panel/form.html"
    success_url = reverse_lazy("panel:lube_list")
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"]="Редактировать смазку"; ctx["back_url"]=reverse_lazy("panel:lube_list")
        return ctx

class LubricantTypeDelete(RoleRequiredMixin, DeleteView):
    allowed_roles = {Role.ADMIN}
    model = LubricantType
    template_name = "panel/delete.html"
    success_url = reverse_lazy("panel:lube_list")
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"]="Удалить смазку"; ctx["back_url"]=reverse_lazy("panel:lube_list")
        return ctx

class SSPSUnitList(RoleRequiredMixin, ListView):
    allowed_roles = {Role.ADMIN}
    model = SSPSUnit
    template_name = "panel/list.html"
    def get_queryset(self):
        return super().get_queryset().select_related("owner").order_by("type_name","number")
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({"title":"Единицы ССПС","create_url":reverse_lazy("panel:ssps_create"),
                    "edit_name":"panel:ssps_edit","delete_name":"panel:ssps_delete"})
        return ctx

class SSPSUnitCreate(RoleRequiredMixin, CreateView):
    allowed_roles = {Role.ADMIN}
    model = SSPSUnit
    form_class = SSPSUnitForm
    template_name = "panel/form.html"
    success_url = reverse_lazy("panel:ssps_list")
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"]="Добавить ССПС"; ctx["back_url"]=reverse_lazy("panel:ssps_list")
        return ctx

class SSPSUnitEdit(RoleRequiredMixin, UpdateView):
    allowed_roles = {Role.ADMIN}
    model = SSPSUnit
    form_class = SSPSUnitForm
    template_name = "panel/form.html"
    success_url = reverse_lazy("panel:ssps_list")
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"]="Редактировать ССПС"; ctx["back_url"]=reverse_lazy("panel:ssps_list")
        return ctx

class SSPSUnitDelete(RoleRequiredMixin, DeleteView):
    allowed_roles = {Role.ADMIN}
    model = SSPSUnit
    template_name = "panel/delete.html"
    success_url = reverse_lazy("panel:ssps_list")
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"]="Удалить ССПС"; ctx["back_url"]=reverse_lazy("panel:ssps_list")
        return ctx

# Бригады
class BrigadeList(RoleRequiredMixin, ListView):
    allowed_roles = {Role.ADMIN}
    model = Brigade
    template_name = "panel/list_brigades.html"

    def get_queryset(self):
        return super().get_queryset().select_related("ssps_unit").prefetch_related("members").order_by(
            "ssps_unit__type_name", "ssps_unit__number", "name"
        )

class BrigadeCreate(RoleRequiredMixin, CreateView):
    allowed_roles = {Role.ADMIN}
    model = Brigade
    form_class = BrigadeForm
    template_name = "panel/form.html"
    success_url = reverse_lazy("panel:brigade_list")
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"]="Добавить бригаду"; ctx["back_url"]=reverse_lazy("panel:brigade_list")
        return ctx

class BrigadeEdit(RoleRequiredMixin, UpdateView):
    allowed_roles = {Role.ADMIN}
    model = Brigade
    form_class = BrigadeForm
    template_name = "panel/form.html"
    success_url = reverse_lazy("panel:brigade_list")
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"]="Редактировать бригаду"; ctx["back_url"]=reverse_lazy("panel:brigade_list")
        return ctx

class BrigadeDelete(RoleRequiredMixin, DeleteView):
    allowed_roles = {Role.ADMIN}
    model = Brigade
    template_name = "panel/delete.html"
    success_url = reverse_lazy("panel:brigade_list")
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"]="Удалить бригаду"; ctx["back_url"]=reverse_lazy("panel:brigade_list")
        return ctx
      
class RouteSheetList(RoleRequiredMixin, ListView):
    allowed_roles = {Role.ADMIN}
    model = RouteSheetAU12
    template_name = "panel/list_routesheets.html"
    
    def get_queryset(self):
        return super().get_queryset().select_related("ssps_unit", "brigade", "created_by").order_by("-date", "-id")
      
class RouteSheetDelete(RoleRequiredMixin, DeleteView):
    allowed_roles = {Role.ADMIN}
    model = RouteSheetAU12
    template_name = "panel/delete.html"
    success_url = reverse_lazy("panel:routesheet_list")
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "Удалить маршрутный лист"
        ctx["back_url"] = reverse_lazy("panel:routesheet_list")
        return ctx