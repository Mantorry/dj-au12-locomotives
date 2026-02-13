from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from apps.directory.models import Station
from .models import Role

User = get_user_model()

def _bootstrapify_form(form: forms.Form) -> forms.Form:
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

class UserRegisterForm(UserCreationForm):
    username = forms.CharField(label="Логин")
    last_name = forms.CharField(label="Фамилия")
    first_name = forms.CharField(label="Имя")
    patronymic = forms.CharField(label="Отчество", required=False)
    role = forms.ChoiceField(label="Должность", choices=Role.choices)

    station = forms.ModelChoiceField(
        label="Станция",
        queryset=Station.objects.all().order_by("name"),
        required=False,
        empty_label="— не выбрана —",
    )

    class Meta:
        model = User
        fields = ("username", "last_name", "first_name", "patronymic", "role", "station")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].label = "Пароль"
        self.fields["password2"].label = "Повторите пароль"
        _bootstrapify_form(self)

class WorkerFilterForm(forms.Form):
    role = forms.ChoiceField(choices=[("", "Все")] + list(Role.choices), required=False, label="Должность")
    q = forms.CharField(required=False, label="Поиск")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _bootstrapify_form(self)
