from django.conf import settings
from django.db import models

from apps.directory.models import (
    SSPSUnit,
    Station,
    FuelType,
    LubricantType,
    Enterprise,
    Brigade,
    Position,
    MachineType,
    WorkType,
    WorkPlace,
    TransportUnit,
)


class AU12Status(models.TextChoices):
    DRAFT = "DRAFT", "Черновик"
    ISSUED = "ISSUED", "Выдан"
    IN_PROGRESS = "IN_PROGRESS", "В работе"
    READY = "READY", "Готов"
    COMPLETED = "COMPLETED", "Выполнен"


class AU12Step(models.TextChoices):
    MED_PRE = "MED_PRE", "Медосмотр (до работы)"
    MASTER_ISSUE = "MASTER_ISSUE", "Выдача мастером"
    CREW_WORK = "CREW_WORK", "Заполнение бригадой"
    MED_POST = "MED_POST", "Медосмотр (после работы)"
    FINAL_REVIEW = "FINAL_REVIEW", "Проверка/закрытие"


class RouteSheetAU12(models.Model):
    number = models.CharField("Номер", max_length=50)
    date = models.DateField("Дата")

    railway_name = models.CharField("Наименование дороги", max_length=255, blank=True)
    
    enterprise = models.ForeignKey(
        Enterprise,
        verbose_name="Предприятие",
        on_delete=models.PROTECT,
        related_name="routesheets",
        null=True,
    )

    ssps_unit = models.ForeignKey(
        SSPSUnit,
        verbose_name="Единица ССПС",
        on_delete=models.PROTECT,
        related_name="au12_routesheets",
    )

    brigade = models.ForeignKey(
        Brigade,
        verbose_name="Бригада",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="routesheets",
    )

    status = models.CharField("Статус", max_length=20, choices=AU12Status.choices, default=AU12Status.DRAFT)
    step = models.CharField("Этап", max_length=20, choices=AU12Step.choices, default=AU12Step.MED_PRE)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Создал",
        on_delete=models.PROTECT,
        related_name="au12_created",
    )
    created_at = models.DateTimeField("Создано", auto_now_add=True)

    class Meta:
        verbose_name = "Маршрутный лист АУ-12"
        verbose_name_plural = "Маршрутные листы АУ-12"
        ordering = ["-date", "-id"]

    def __str__(self) -> str:
        return f"АУ-12 №{self.number} от {self.date}"

    # ─────────────────────────────
    # флаги заполненности секций

    def is_med_pre_done(self) -> bool:
        return hasattr(self, "medical") and self.medical.pre_allowed is True

    def is_section_i_done(self) -> bool:
        return self.crew_rows.exists()

    def is_section_ii_done(self) -> bool:
        if not hasattr(self, "section_ii"):
            return False
        s2 = self.section_ii
        return s2.speedometer_out_km is not None and s2.speedometer_in_km is not None

    def is_section_iii_done(self) -> bool:
        return self.work_rows.exists()

    def is_section_iv_done(self) -> bool:
        return hasattr(self, "section_iv") and self.section_iv.is_done

    def is_section_v_done(self) -> bool:
        return hasattr(self, "section_v") and self.section_v.is_done

    def is_section_vi_done(self) -> bool:
        return hasattr(self, "section_vi") and self.section_vi.is_done

    def is_med_post_done(self) -> bool:
        return hasattr(self, "medical") and self.medical.post_allowed is True

    def is_fully_done(self) -> bool:
        return (
            self.is_med_pre_done()
            and self.is_section_i_done()
            and self.is_section_ii_done()
            and self.is_section_iii_done()
            and self.is_section_iv_done()
            and self.is_section_v_done()
            and self.is_section_vi_done()
            and self.is_med_post_done()
        )


class AU12MedicalCheck(models.Model):
    routesheet = models.OneToOneField(
        RouteSheetAU12,
        verbose_name="Маршрутный лист",
        on_delete=models.CASCADE,
        related_name="medical",
    )

    pre_time = models.TimeField("Время медосмотра (до)", null=True, blank=True)
    pre_allowed = models.BooleanField("Допущен (до)", default=False)
    pre_medic_name = models.CharField("Медик (до)", max_length=255, blank=True)

    post_time = models.TimeField("Время медосмотра (после)", null=True, blank=True)
    post_allowed = models.BooleanField("Допущен (после)", default=False)
    post_medic_name = models.CharField("Медик (после)", max_length=255, blank=True)

    class Meta:
        verbose_name = "Медосмотр"
        verbose_name_plural = "Медосмотры"


class AU12CrewRow(models.Model):
    routesheet = models.ForeignKey(
        RouteSheetAU12,
        verbose_name="Маршрутный лист",
        on_delete=models.CASCADE,
        related_name="crew_rows",
    )

    position_ref = models.ForeignKey(
        Position,
        verbose_name="Должность (из справочника)",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    position_text = models.CharField("Должность (вручную)", max_length=120, blank=True)

    full_name = models.CharField("ФИО", max_length=255)
    time_check_in = models.TimeField("Явка", null=True, blank=True)
    time_check_out = models.TimeField("Окончание", null=True, blank=True)
    overtime_minutes = models.PositiveIntegerField("Переработка (мин)", default=0)
    rest_minutes = models.PositiveIntegerField("Отдых (мин)", default=0)
    overtime_reason = models.CharField("Причина переработки", max_length=255, blank=True)
    responsible_person = models.CharField("Ответственный", max_length=255, blank=True)

    class Meta:
        verbose_name = "Строка бригады"
        verbose_name_plural = "Бригада (строки)"

    @property
    def position_display(self) -> str:
        return (self.position_ref.name if self.position_ref else "") or self.position_text


class AU12SectionII(models.Model):
    routesheet = models.OneToOneField(
        "RouteSheetAU12",
        verbose_name="Маршрутный лист",
        on_delete=models.CASCADE,
        related_name="section_ii",
    )

    # ТОЛЬКО ВЫБОР: тип машины + номер машины (транспорт)
    machine_type = models.ForeignKey(
        MachineType,
        verbose_name="Тип машины",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    transport = models.ForeignKey(
        TransportUnit,
        verbose_name="Номер машины",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    # пробег
    speedometer_out_km = models.PositiveIntegerField("Спидометр (выезд), км", null=True, blank=True)
    moto_hours_out = models.DecimalField("Моточасы (выезд)", max_digits=8, decimal_places=1, null=True, blank=True)

    speedometer_in_km = models.PositiveIntegerField("Спидометр (возврат), км", null=True, blank=True)
    moto_hours_in = models.DecimalField("Моточасы (возврат)", max_digits=8, decimal_places=1, null=True, blank=True)

    # тсм
    fuel_type = models.ForeignKey(FuelType, verbose_name="Марка топлива", on_delete=models.PROTECT, null=True, blank=True)
    fuel_issued_l = models.DecimalField("Выдано топлива, л", max_digits=9, decimal_places=2, default=0)
    fuel_left_out_l = models.DecimalField("Остаток топлива при выезде, л", max_digits=9, decimal_places=2, default=0)
    fuel_left_in_l = models.DecimalField("Остаток топлива при возврате, л", max_digits=9, decimal_places=2, default=0)

    lubricant_type = models.ForeignKey(LubricantType, verbose_name="Марка смазки", on_delete=models.PROTECT, null=True, blank=True)
    lubricant_issued = models.DecimalField("Выдано смазки", max_digits=9, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Раздел II"
        verbose_name_plural = "Раздел II"


class AU12WorkRow(models.Model):
    routesheet = models.ForeignKey(
        RouteSheetAU12,
        verbose_name="Маршрутный лист",
        on_delete=models.CASCADE,
        related_name="work_rows",
    )

    request_no = models.CharField("№ заявки", max_length=50, blank=True)
    station_from = models.ForeignKey(
        Station, verbose_name="Станция отправления", on_delete=models.PROTECT, related_name="+", null=True, blank=True
    )
    station_to = models.ForeignKey(
        Station, verbose_name="Станция назначения", on_delete=models.PROTECT, related_name="+", null=True, blank=True
    )

    time_departure = models.TimeField("Отправление", null=True, blank=True)
    time_arrival = models.TimeField("Прибытие", null=True, blank=True)

    work_type_ref = models.ForeignKey(WorkType, verbose_name="Вид работ (из справочника)", on_delete=models.PROTECT, null=True, blank=True)
    work_name = models.CharField("Наименование работ (вручную)", max_length=255, blank=True)

    work_place_ref = models.ForeignKey(
        WorkPlace, verbose_name="Место работ (из справочника)", on_delete=models.PROTECT, null=True, blank=True
    )
    work_place = models.CharField("Место работ (вручную)", max_length=255, blank=True)

    machine_work_start = models.TimeField("Начало работы машины", null=True, blank=True)
    machine_work_end = models.TimeField("Окончание работы машины", null=True, blank=True)

    work_volume = models.CharField("Объём работ", max_length=120, blank=True)
    supervisor_signature = models.CharField("Подпись руководителя", max_length=255, blank=True)

    class Meta:
        verbose_name = "Строка работ"
        verbose_name_plural = "Работы (раздел III)"

    @property
    def work_display(self) -> str:
        return (self.work_type_ref.name if self.work_type_ref else "") or self.work_name

    @property
    def work_place_display(self) -> str:
        return (self.work_place_ref.name if self.work_place_ref else "") or self.work_place


# ─────────────────────────────────────────────────────────────
# Раздел IV–VI: вернул как отдельные модели OneToOne
# (структура универсальная, но с полями “под бланк”: отметки/замечания/подписи)

class AU12SectionIV(models.Model):
    routesheet = models.OneToOneField(
        RouteSheetAU12,
        verbose_name="Маршрутный лист",
        on_delete=models.CASCADE,
        related_name="section_iv",
    )

    technical_state = models.TextField("Техническое состояние/замечания (раздел IV)", blank=True)
    defects_found = models.TextField("Выявленные неисправности", blank=True)
    measures_taken = models.TextField("Принятые меры", blank=True)

    responsible_name = models.CharField("Ответственный (ФИО)", max_length=255, blank=True)
    responsible_signature = models.CharField("Подпись ответственного", max_length=255, blank=True)
    sign_time = models.TimeField("Время отметки", null=True, blank=True)

    is_done = models.BooleanField("Раздел IV заполнен", default=False)

    class Meta:
        verbose_name = "Раздел IV"
        verbose_name_plural = "Раздел IV"


class AU12SectionV(models.Model):
    routesheet = models.OneToOneField(
        RouteSheetAU12,
        verbose_name="Маршрутный лист",
        on_delete=models.CASCADE,
        related_name="section_v",
    )

    fuel_notes = models.TextField("Примечания по топливу/ТСМ (раздел V)", blank=True)
    repairs_notes = models.TextField("Примечания по ремонту/обслуживанию", blank=True)

    master_name = models.CharField("Мастер (ФИО)", max_length=255, blank=True)
    master_signature = models.CharField("Подпись мастера", max_length=255, blank=True)
    sign_time = models.TimeField("Время отметки", null=True, blank=True)

    is_done = models.BooleanField("Раздел V заполнен", default=False)

    class Meta:
        verbose_name = "Раздел V"
        verbose_name_plural = "Раздел V"


class AU12SectionVI(models.Model):
    routesheet = models.OneToOneField(
        RouteSheetAU12,
        verbose_name="Маршрутный лист",
        on_delete=models.CASCADE,
        related_name="section_vi",
    )

    final_notes = models.TextField("Итоговые замечания (раздел VI)", blank=True)

    inspector_name = models.CharField("Проверил (ФИО)", max_length=255, blank=True)
    inspector_signature = models.CharField("Подпись проверившего", max_length=255, blank=True)
    sign_time = models.TimeField("Время отметки", null=True, blank=True)

    is_done = models.BooleanField("Раздел VI заполнен", default=False)

    class Meta:
        verbose_name = "Раздел VI"
        verbose_name_plural = "Раздел VI"
