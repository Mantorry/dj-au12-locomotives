from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.directory.models import Station

class Role(models.TextChoices):
    ADMIN = "ADMIN", "Администратор"
    MASTER = "MASTER", "Мастер"
    MACHINIST = "MACHINIST", "Машинист"
    ASSISTANT = "ASSISTANT", "Помощник машиниста"
    MEDIC = "MEDIC", "Медик"
    INSPECTOR = "INSPECTOR", "Инспектор/ревизор"

class User(AbstractUser):
    patronymic = models.CharField("Отчество", max_length=150, blank=True, default="")
    role = models.CharField("Должность", max_length=20, choices=Role.choices, default=Role.MACHINIST)

    station = models.ForeignKey(
        Station,
        verbose_name="Станция",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="users",
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        fio = " ".join([self.last_name or "", self.first_name or "", self.patronymic or ""]).strip()
        return fio or self.username

    @property
    def is_admin(self) -> bool:
        return self.is_superuser or self.role == Role.ADMIN
