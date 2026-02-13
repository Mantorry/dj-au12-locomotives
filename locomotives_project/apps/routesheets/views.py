from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, DetailView

from apps.accounts.permissions import RoleRequiredMixin
from apps.accounts.models import Role

from .models import (
    RouteSheetAU12,
    AU12MedicalCheck,
    AU12SectionII,
    AU12SectionIV,
    AU12SectionV,
    AU12SectionVI,
    AU12Step,
)
from .forms import (
    AU12CreateForm,
    MedicalPreForm,
    MedicalPostForm,
    CrewFormSet,
    AU12SectionIIForm,
    WorkFormSet,
    AU12SectionIVForm,
    AU12SectionVForm,
    AU12SectionVIForm,
    bootstrapify_formset,
)
from .services.workflow import can_access_step, recalc_status_and_step, mark_issued_by_master, finalize_routesheet
from .services.prefill import prefill_section_ii_from_previous
from .services.prefill_crew_from_brigade import prefill_crew_from_brigade
from .services.export_pdf import export_au12_pdf
from .services.export_excel import export_au12_excel
from .services.analytics import run_km, fuel_consumed_l, consumption_l_per_100km
from apps.directory.models import SSPSUnit


User = get_user_model()


def _require_access(request, rs: RouteSheetAU12, step: str) -> None:
    if not can_access_step(request.user, rs, step):
        raise Http404("Недостаточно прав или неверная последовательность заполнения.")


class AU12ListView(RoleRequiredMixin, ListView):
    allowed_roles = {Role.ADMIN, Role.MASTER, Role.MACHINIST, Role.ASSISTANT, Role.MEDIC, Role.INSPECTOR}
    model = RouteSheetAU12
    template_name = "routesheets/au12_list.html"
    paginate_by = 50

    def get_queryset(self):
        qs = (
            super()
            .get_queryset()
            .select_related("ssps_unit", "brigade")
            .order_by("-date", "-id")
        )
        q = (self.request.GET.get("q") or "").strip()
        if q:
            qs = qs.filter(
                Q(number__icontains=q)
                | Q(ssps_unit__type_name__icontains=q)
                | Q(ssps_unit__number__icontains=q)
                | Q(brigade__name__icontains=q)
            )
        return qs


class AU12CreateView(RoleRequiredMixin, CreateView):
    allowed_roles = {Role.ADMIN, Role.MASTER}
    model = RouteSheetAU12
    form_class = AU12CreateForm
    template_name = "routesheets/au12_create.html"
    success_url = reverse_lazy("routesheets:au12_list")

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.created_by = self.request.user
        obj.save()
        form.save_m2m()

        # создаём медосмотр-запись сразу
        AU12MedicalCheck.objects.get_or_create(routesheet=obj)

        messages.success(self.request, "Лист создан.")
        return redirect("routesheets:au12_detail", pk=obj.pk)


class AU12DetailView(RoleRequiredMixin, DetailView):
    allowed_roles = {Role.ADMIN, Role.MASTER, Role.MACHINIST, Role.ASSISTANT, Role.MEDIC, Role.INSPECTOR}
    model = RouteSheetAU12
    template_name = "routesheets/au12_detail.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        rs: RouteSheetAU12 = self.object

        ctx["can_med_pre"] = can_access_step(self.request.user, rs, AU12Step.MED_PRE)
        ctx["can_issue"] = can_access_step(self.request.user, rs, AU12Step.MASTER_ISSUE)
        ctx["can_med_post"] = can_access_step(self.request.user, rs, AU12Step.MED_POST)
        ctx["can_finalize"] = can_access_step(self.request.user, rs, AU12Step.FINAL_REVIEW)

        # кнопки разделов (бригада/мастер — в рамках этапа CREW_WORK)
        role = getattr(self.request.user, "role", None)
        ctx["can_sections"] = (
            getattr(self.request.user, "is_superuser", False)
            or role in {Role.ADMIN, Role.MASTER, Role.MACHINIST, Role.ASSISTANT, Role.INSPECTOR}
        )
        return ctx


def au12_med_pre(request, pk: int):
    rs = get_object_or_404(RouteSheetAU12, pk=pk)
    _require_access(request, rs, AU12Step.MED_PRE)

    med, _ = AU12MedicalCheck.objects.get_or_create(routesheet=rs)

    if request.method == "POST":
        form = MedicalPreForm(request.POST, instance=med)
        if form.is_valid():
            form.save()
            recalc_status_and_step(rs)
            rs.save(update_fields=["status", "step"])
            messages.success(request, "Медосмотр (до) сохранён.")
            return redirect("routesheets:au12_detail", pk=rs.pk)
    else:
        form = MedicalPreForm(instance=med)

    return render(request, "routesheets/au12_med_pre.html", {"rs": rs, "form": form})


def au12_issue_by_master(request, pk: int):
    rs = get_object_or_404(RouteSheetAU12, pk=pk)
    _require_access(request, rs, AU12Step.MASTER_ISSUE)

    if request.method != "POST":
        return redirect("routesheets:au12_detail", pk=rs.pk)

    # префиллы
    prefill_section_ii_from_previous(rs)
    prefill_crew_from_brigade(rs)

    mark_issued_by_master(rs)
    rs.save(update_fields=["status", "step"])
    messages.success(request, "Лист выдан мастером. Доступно заполнение бригадой.")
    return redirect("routesheets:au12_detail", pk=rs.pk)


def au12_section_i(request, pk: int):
    rs = get_object_or_404(RouteSheetAU12, pk=pk)
    _require_access(request, rs, AU12Step.CREW_WORK)

    qs = rs.crew_rows.all()
    if request.method == "POST":
        formset = CrewFormSet(request.POST, instance=rs, queryset=qs)
        bootstrapify_formset(formset)
        if formset.is_valid():
            formset.save()
            recalc_status_and_step(rs)
            rs.save(update_fields=["status", "step"])
            messages.success(request, "Раздел I сохранён.")
            return redirect("routesheets:au12_detail", pk=rs.pk)
    else:
        formset = CrewFormSet(instance=rs, queryset=qs)
        bootstrapify_formset(formset)

    return render(request, "routesheets/au12_section_i.html", {"rs": rs, "formset": formset})


def au12_section_ii(request, pk: int):
    rs = get_object_or_404(RouteSheetAU12, pk=pk)
    _require_access(request, rs, AU12Step.CREW_WORK)

    obj, _ = AU12SectionII.objects.get_or_create(routesheet=rs)

    if request.method == "POST":
        form = AU12SectionIIForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            recalc_status_and_step(rs)
            rs.save(update_fields=["status", "step"])
            messages.success(request, "Раздел II сохранён.")
            return redirect("routesheets:au12_detail", pk=rs.pk)
    else:
        form = AU12SectionIIForm(instance=obj)

    return render(request, "routesheets/au12_section_ii.html", {"rs": rs, "form": form})


def au12_section_iii(request, pk: int):
    rs = get_object_or_404(RouteSheetAU12, pk=pk)
    _require_access(request, rs, AU12Step.CREW_WORK)

    qs = rs.work_rows.all()
    if request.method == "POST":
        formset = WorkFormSet(request.POST, instance=rs, queryset=qs)
        bootstrapify_formset(formset)
        if formset.is_valid():
            formset.save()
            recalc_status_and_step(rs)
            rs.save(update_fields=["status", "step"])
            messages.success(request, "Раздел III сохранён.")
            return redirect("routesheets:au12_detail", pk=rs.pk)
    else:
        formset = WorkFormSet(instance=rs, queryset=qs)
        bootstrapify_formset(formset)

    return render(request, "routesheets/au12_section_iii.html", {"rs": rs, "formset": formset})


def au12_section_iv(request, pk: int):
    rs = get_object_or_404(RouteSheetAU12, pk=pk)
    _require_access(request, rs, AU12Step.CREW_WORK)

    obj, _ = AU12SectionIV.objects.get_or_create(routesheet=rs)

    if request.method == "POST":
        form = AU12SectionIVForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            recalc_status_and_step(rs)
            rs.save(update_fields=["status", "step"])
            messages.success(request, "Раздел IV сохранён.")
            return redirect("routesheets:au12_detail", pk=rs.pk)
    else:
        form = AU12SectionIVForm(instance=obj)

    return render(request, "routesheets/au12_section_iv.html", {"rs": rs, "form": form})


def au12_section_v(request, pk: int):
    rs = get_object_or_404(RouteSheetAU12, pk=pk)
    _require_access(request, rs, AU12Step.CREW_WORK)

    obj, _ = AU12SectionV.objects.get_or_create(routesheet=rs)

    if request.method == "POST":
        form = AU12SectionVForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            recalc_status_and_step(rs)
            rs.save(update_fields=["status", "step"])
            messages.success(request, "Раздел V сохранён.")
            return redirect("routesheets:au12_detail", pk=rs.pk)
    else:
        form = AU12SectionVForm(instance=obj)

    return render(request, "routesheets/au12_section_v.html", {"rs": rs, "form": form})


def au12_section_vi(request, pk: int):
    rs = get_object_or_404(RouteSheetAU12, pk=pk)
    _require_access(request, rs, AU12Step.CREW_WORK)

    obj, _ = AU12SectionVI.objects.get_or_create(routesheet=rs)

    if request.method == "POST":
        form = AU12SectionVIForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            recalc_status_and_step(rs)
            rs.save(update_fields=["status", "step"])
            messages.success(request, "Раздел VI сохранён.")
            return redirect("routesheets:au12_detail", pk=rs.pk)
    else:
        form = AU12SectionVIForm(instance=obj)

    return render(request, "routesheets/au12_section_vi.html", {"rs": rs, "form": form})


def au12_med_post(request, pk: int):
    rs = get_object_or_404(RouteSheetAU12, pk=pk)
    _require_access(request, rs, AU12Step.MED_POST)

    med, _ = AU12MedicalCheck.objects.get_or_create(routesheet=rs)

    if request.method == "POST":
        form = MedicalPostForm(request.POST, instance=med)
        if form.is_valid():
            form.save()
            recalc_status_and_step(rs)
            rs.save(update_fields=["status", "step"])
            messages.success(request, "Медосмотр (после) сохранён.")
            return redirect("routesheets:au12_detail", pk=rs.pk)
    else:
        form = MedicalPostForm(instance=med)

    return render(request, "routesheets/au12_med_post.html", {"rs": rs, "form": form})


def au12_finalize(request, pk: int):
    rs = get_object_or_404(RouteSheetAU12, pk=pk)
    _require_access(request, rs, AU12Step.FINAL_REVIEW)

    if request.method != "POST":
        return redirect("routesheets:au12_detail", pk=rs.pk)

    if not rs.is_fully_done():
        messages.error(request, "Нельзя закрыть: лист заполнен не полностью.")
        return redirect("routesheets:au12_detail", pk=rs.pk)

    finalize_routesheet(rs)
    rs.save(update_fields=["status", "step"])
    messages.success(request, "Лист закрыт.")
    return redirect("routesheets:au12_detail", pk=rs.pk)


def au12_export_pdf(request, pk: int):
    rs = get_object_or_404(RouteSheetAU12, pk=pk)
    # экспорт разрешим всем, кто видит лист
    data = export_au12_pdf(rs)
    resp = HttpResponse(data, content_type="application/pdf")
    resp["Content-Disposition"] = f'attachment; filename="AU12_{rs.number}_{rs.date}.pdf"'
    return resp


def au12_export_excel(request, pk: int):
    rs = get_object_or_404(RouteSheetAU12, pk=pk)
    data = export_au12_excel(rs)
    resp = HttpResponse(
        data,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    resp["Content-Disposition"] = f'attachment; filename="AU12_{rs.number}_{rs.date}.xlsx"'
    return resp


def analytics_fuel(request):
    # доступ: мастер/админ/инспектор
    if not request.user.is_authenticated:
        raise Http404()
    if not (request.user.is_superuser or request.user.role in {Role.ADMIN, Role.MASTER, Role.INSPECTOR}):
        raise Http404()

    date_from = (request.GET.get("date_from") or "").strip()
    date_to = (request.GET.get("date_to") or "").strip()
    ssps = (request.GET.get("ssps") or "").strip()

    qs = RouteSheetAU12.objects.select_related("ssps_unit").all()
    if date_from:
        qs = qs.filter(date__gte=date_from)
    if date_to:
        qs = qs.filter(date__lte=date_to)
    if ssps:
        qs = qs.filter(ssps_unit_id=ssps)

    rows = []
    for rs in qs.order_by("-date", "-id")[:500]:
        km = run_km(rs)
        fuel = float(fuel_consumed_l(rs))
        l100 = consumption_l_per_100km(rs)
        rows.append({"date": rs.date, "number": rs.number, "ssps": str(rs.ssps_unit), "km": km, "fuel": fuel, "l_100": l100})

    ssps_list = SSPSUnit.objects.order_by("type_name", "number")
    return render(
        request,
        "routesheets/analytics_fuel.html",
        {"rows": rows, "filters": {"date_from": date_from, "date_to": date_to, "ssps": ssps}, "ssps_list": ssps_list},
    )
