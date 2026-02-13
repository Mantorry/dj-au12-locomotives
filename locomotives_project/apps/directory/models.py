from django.db import models
from django.conf import settings

class Enterprise(models.Model):
    name = models.CharField("Наименование предприятия", max_length=255, unique=True)

    class Meta:
        verbose_name = "Предприятие"
        verbose_name_plural = "Предприятия"

    def __str__(self): return self.name

class Station(models.Model):
    name = models.CharField("Станция", max_length=255, unique=True)

    class Meta:
        verbose_name = "Станция"
        verbose_name_plural = "Станции"

    def __str__(self): return self.name

class FuelType(models.Model):
    name = models.CharField("Марка топлива", max_length=100, unique=True)

    class Meta:
        verbose_name = "Топливо"
        verbose_name_plural = "Топливо"

    def __str__(self): return self.name

class LubricantType(models.Model):
    name = models.CharField("Марка смазки", max_length=100, unique=True)

    class Meta:
        verbose_name = "Смазка"
        verbose_name_plural = "Смазочные материалы"

    def __str__(self): return self.name

class SSPSUnit(models.Model):
    owner = models.ForeignKey(Enterprise, verbose_name="Владелец (предприятие)", on_delete=models.PROTECT)
    type_name = models.CharField("Тип ССПС", max_length=120)
    number = models.CharField("Номер ССПС", max_length=50)
    max_people = models.PositiveIntegerField("Макс. число людей", default=0)

    class Meta:
        verbose_name = "Единица ССПС"
        verbose_name_plural = "Единицы ССПС"
        unique_together = [("type_name", "number")]

    def __str__(self):
        return f"{self.type_name} №{self.number}"

class Position(models.Model):
    name = models.CharField("Должность (справочник)", max_length=120, unique=True)

    class Meta:
        verbose_name = "Должность"
        verbose_name_plural = "Должности"

    def __str__(self): return self.name

class MachineType(models.Model):
    name = models.CharField("Тип машины (справочник)", max_length=120, unique=True)

    class Meta:
        verbose_name = "Тип машины"
        verbose_name_plural = "Типы машин"

    def __str__(self): return self.name

class WorkType(models.Model):
    name = models.CharField("Вид работ (справочник)", max_length=255, unique=True)

    class Meta:
        verbose_name = "Вид работ"
        verbose_name_plural = "Виды работ"

    def __str__(self): return self.name

class WorkPlace(models.Model):
    name = models.CharField("Место работ (справочник)", max_length=255, unique=True)

    class Meta:
        verbose_name = "Место работ"
        verbose_name_plural = "Места работ"

    def __str__(self): return self.name

class Brigade(models.Model):
    name = models.CharField("Название бригады", max_length=255)
    ssps_unit = models.ForeignKey(SSPSUnit, verbose_name="Единица ССПС", on_delete=models.PROTECT, related_name="brigades")
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name="Состав бригады (работники)",
        related_name="brigades",
        blank=True
    )
    is_active = models.BooleanField("Активна", default=True)

    class Meta:
        verbose_name = "Бригада"
        verbose_name_plural = "Бригады"
        unique_together = [("name", "ssps_unit")]

    def __str__(self):
        return f"{self.name} ({self.ssps_unit})"
      
class TransportUnit(models.Model):
    """
    Конкретная машина/транспорт (тип + номер).
    Нужна для раздела II: два поля (тип машины и номер машины).
    При желании можно привязать транспорт к ССПС.
    """
    machine_type = models.ForeignKey(
        MachineType,
        verbose_name="Тип машины",
        on_delete=models.PROTECT,
        related_name="transports",
    )
    number = models.CharField("Номер машины", max_length=50)

    # опционально: если транспорт закреплён за ССПС
    ssps_unit = models.ForeignKey(
        SSPSUnit,
        verbose_name="ССПС",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="transports",
    )

    is_active = models.BooleanField("Активен", default=True)

    class Meta:
        verbose_name = "Транспорт"
        verbose_name_plural = "Транспорт"
        unique_together = [("machine_type", "number")]

    def __str__(self):
        return f"{self.machine_type} №{self.number}"
