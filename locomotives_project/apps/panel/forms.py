from django import forms
from django.contrib.auth import get_user_model

from apps.accounts.models import Role
from apps.directory.models import (
    Enterprise, Station, FuelType, LubricantType, SSPSUnit,
    Brigade
)

User = get_user_model()

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

class UserEditForm(forms.ModelForm):
    role = forms.ChoiceField(label="Должность", choices=Role.choices)

    class Meta:
        model = User
        fields = ["username", "last_name", "first_name", "patronymic", "role", "station", "is_active"]
        labels = {
            "username": "Логин",
            "last_name": "Фамилия",
            "first_name": "Имя",
            "patronymic": "Отчество",
            "role": "Должность",
            "station": "Станция",
            "is_active": "Активен",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["station"].queryset = Station.objects.all().order_by("name")
        bootstrapify_form(self)

class EnterpriseForm(forms.ModelForm):
    class Meta:
        model = Enterprise
        fields = ["name"]
        labels = {"name": "Наименование предприятия"}
    def __init__(self,*a,**k): super().__init__(*a,**k); bootstrapify_form(self)

class StationForm(forms.ModelForm):
    class Meta:
        model = Station
        fields = ["name"]
        labels = {"name": "Станция"}
    def __init__(self,*a,**k): super().__init__(*a,**k); bootstrapify_form(self)

class FuelTypeForm(forms.ModelForm):
    class Meta:
        model = FuelType
        fields = ["name"]
        labels = {"name": "Марка топлива"}
    def __init__(self,*a,**k): super().__init__(*a,**k); bootstrapify_form(self)

class LubricantTypeForm(forms.ModelForm):
    class Meta:
        model = LubricantType
        fields = ["name"]
        labels = {"name": "Марка смазки"}
    def __init__(self,*a,**k): super().__init__(*a,**k); bootstrapify_form(self)

class SSPSUnitForm(forms.ModelForm):
    class Meta:
        model = SSPSUnit
        fields = ["owner", "type_name", "number", "max_people"]
        labels = {
            "owner": "Владелец (предприятие)",
            "type_name": "Тип ССПС",
            "number": "Номер ССПС",
            "max_people": "Макс. число людей",
        }
    def __init__(self,*a,**k): super().__init__(*a,**k); bootstrapify_form(self)

class BrigadeForm(forms.ModelForm):
    class Meta:
        model = Brigade
        fields = ["name", "ssps_unit", "members", "is_active"]
        labels = {
            "name": "Название бригады",
            "ssps_unit": "Единица ССПС",
            "members": "Состав бригады",
            "is_active": "Активна",
        }
        widgets = {"members": forms.SelectMultiple(attrs={"size": "12"})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # по умолчанию — все активные пользователи
        self.fields["members"].queryset = User.objects.filter(is_active=True).order_by(
            "last_name", "first_name", "patronymic", "username"
        )
        bootstrapify_form(self)