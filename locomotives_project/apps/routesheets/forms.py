from django import forms
from django.forms import inlineformset_factory

from apps.directory.models import Enterprise, MachineType, TransportUnit
from .models import (
    RouteSheetAU12,
    AU12MedicalCheck,
    AU12CrewRow,
    AU12SectionII,
    AU12WorkRow,
    AU12SectionIV,
    AU12SectionV,
    AU12SectionVI,
)


def bootstrapify_form(form: forms.Form) -> forms.Form:
    for _, f in form.fields.items():
        cls = f.widget.attrs.get("class", "")
        if "form-control" in cls or "form-select" in cls or "form-check-input" in cls:
            continue

        if f.widget.__class__.__name__ in ["Select", "SelectMultiple"]:
            f.widget.attrs["class"] = (cls + " form-select").strip()
        elif f.widget.__class__.__name__ in ["CheckboxInput"]:
            f.widget.attrs["class"] = (cls + " form-check-input").strip()
        else:
            f.widget.attrs["class"] = (cls + " form-control").strip()
    return form


def bootstrapify_formset(formset) -> None:
    for form in formset.forms:
        bootstrapify_form(form)


class AU12CreateForm(forms.ModelForm):
    class Meta:
        model = RouteSheetAU12
        fields = ["number", "date", "railway_name", "enterprise", "ssps_unit", "brigade"]
        labels = {
            "number": "Номер",
            "date": "Дата",
            "railway_name": "Наименование дороги",
            "enterprise": "Предприятие",
            "ssps_unit": "Единица ССПС",
            "brigade": "Бригада",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['enterprise'].queryset = Enterprise.objects.order_by("name")
        self.fields['enterprise'].empty_laber = '-- выберите предприятие --'

        if "brigade" in self.fields:
            self.fields["brigade"].queryset = (
                self.fields["brigade"].queryset.select_related("ssps_unit").filter(is_active=True)
            )

        bootstrapify_form(self)

    def clean(self):
        cleaned = super().clean()
        ssps = cleaned.get("ssps_unit")
        brigade = cleaned.get("brigade")
        if brigade and ssps and brigade.ssps_unit_id != ssps.id:
            self.add_error("brigade", "Выбранная бригада не принадлежит выбранному ССПС.")
        return cleaned


class MedicalPreForm(forms.ModelForm):
    class Meta:
        model = AU12MedicalCheck
        fields = ["pre_time", "pre_allowed", "pre_medic_name"]
        labels = {"pre_time": "Время (до)", "pre_allowed": "Допущен (до)", "pre_medic_name": "Медик (до)"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bootstrapify_form(self)


class MedicalPostForm(forms.ModelForm):
    class Meta:
        model = AU12MedicalCheck
        fields = ["post_time", "post_allowed", "post_medic_name"]
        labels = {
            "post_time": "Время (после)",
            "post_allowed": "Допущен (после)",
            "post_medic_name": "Медик (после)",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bootstrapify_form(self)


CrewFormSet = inlineformset_factory(
    RouteSheetAU12,
    AU12CrewRow,
    fields=[
        "position_ref",
        "position_text",
        "full_name",
        "time_check_in",
        "time_check_out",
        "overtime_minutes",
        "rest_minutes",
        "overtime_reason",
        "responsible_person",
    ],
    extra=3,
    can_delete=True,
)


class AU12SectionIIForm(forms.ModelForm):
    class Meta:
        model = AU12SectionII
        fields = [
            "machine_type",
            "transport",
            "speedometer_out_km",
            "moto_hours_out",
            "speedometer_in_km",
            "moto_hours_in",
            "fuel_type",
            "fuel_issued_l",
            "fuel_left_out_l",
            "fuel_left_in_l",
            "lubricant_type",
            "lubricant_issued",
        ]
        labels = {
            "machine_type": "Тип машины",
            "transport": "Номер машины",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["machine_type"].queryset = MachineType.objects.order_by("name")
        self.fields["transport"].queryset = TransportUnit.objects.filter(is_active=True).select_related("machine_type").order_by("machine_type__name", "number")

        bootstrapify_form(self)

    def clean(self):
        cleaned = super().clean()
        mt = cleaned.get("machine_type")
        tr = cleaned.get("transport")
        if mt and tr and tr.machine_type_id != mt.id:
            self.add_error("transport", "Номер машины не соответствует выбранному типу.")
        return cleaned


WorkFormSet = inlineformset_factory(
    RouteSheetAU12,
    AU12WorkRow,
    fields=[
        "request_no",
        "station_from",
        "station_to",
        "time_departure",
        "time_arrival",
        "work_type_ref",
        "work_name",
        "work_place_ref",
        "work_place",
        "machine_work_start",
        "machine_work_end",
        "work_volume",
        "supervisor_signature",
    ],
    extra=3,
    can_delete=True,
)


class AU12SectionIVForm(forms.ModelForm):
    class Meta:
        model = AU12SectionIV
        exclude = ["routesheet"]
        labels = {
            "technical_state": "Техническое состояние/замечания",
            "defects_found": "Неисправности",
            "measures_taken": "Принятые меры",
            "responsible_name": "Ответственный (ФИО)",
            "responsible_signature": "Подпись ответственного",
            "sign_time": "Время",
            "is_done": "Раздел IV заполнен",
        }
        widgets = {
            "technical_state": forms.Textarea(attrs={"rows": 3}),
            "defects_found": forms.Textarea(attrs={"rows": 3}),
            "measures_taken": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bootstrapify_form(self)


class AU12SectionVForm(forms.ModelForm):
    class Meta:
        model = AU12SectionV
        exclude = ["routesheet"]
        labels = {
            "fuel_notes": "Примечания по топливу/ТСМ",
            "repairs_notes": "Примечания по ремонту/обслуживанию",
            "master_name": "Мастер (ФИО)",
            "master_signature": "Подпись мастера",
            "sign_time": "Время",
            "is_done": "Раздел V заполнен",
        }
        widgets = {
            "fuel_notes": forms.Textarea(attrs={"rows": 3}),
            "repairs_notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bootstrapify_form(self)


class AU12SectionVIForm(forms.ModelForm):
    class Meta:
        model = AU12SectionVI
        exclude = ["routesheet"]
        labels = {
            "final_notes": "Итоговые замечания",
            "inspector_name": "Проверил (ФИО)",
            "inspector_signature": "Подпись проверившего",
            "sign_time": "Время",
            "is_done": "Раздел VI заполнен",
        }
        widgets = {"final_notes": forms.Textarea(attrs={"rows": 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bootstrapify_form(self)
