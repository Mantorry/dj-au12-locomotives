import io

from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


def _reg_fonts():
    font_path = settings.BASE_DIR / "static" / "fonts" / "DejaVuSans.ttf"
    pdfmetrics.registerFont(TTFont("DejaVuSans", str(font_path)))


def export_au12_pdf(rs) -> bytes:
    _reg_fonts()
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    c.setFont("DejaVuSans", 9)

    width, height = A4
    x0, y0 = 28, height - 32

    def v(val):
        return val if val not in [None, ""] else "—"

    def line(text, dy=14, bold=False):
        nonlocal y0
        c.setFont("DejaVuSans", 9 if not bold else 10)
        c.drawString(x0, y0, str(text))
        y0 -= dy

    def ensure_space(h):
        nonlocal y0
        if y0 - h < 30:
            c.setFont("DejaVuSans", 9)
            y0 = height - 32

    line("Маршрутный лист формы АУ-12", dy=16, bold=True)
    line(f"№ {rs.number} от {rs.date}", dy=16)
    
    line(f"Дорога: {rs.railway_name}")
    line(f"Предприятие: {rs.enterprise.name if rs.enterprise else '—'}")
    line(f"ССПС: {rs.ssps_unit}")
    line(f"Бригада: {rs.brigade.name if rs.brigade else '—'}", dy=16)

    # Раздел I
    line("Раздел I — Бригада", bold=True)
    for idx, r in enumerate(rs.crew_rows.all(), start=1):
        line(
            f"{idx}. {v(r.position_display)} | {v(r.full_name)} | Явка: {v(r.time_check_in)} | "
            f"Оконч.: {v(r.time_check_out)} | Перер.: {v(r.overtime_minutes)} | Отдых: {v(r.rest_minutes)}"        
        )
        
    ensure_space(130)
    # Раздел II
    line("Раздел II — Пробег, моточасы, ТСМ", dy=14, bold=True)
    s2 = getattr(rs, "section_ii", None)
    if s2:
        owner_name = "—"
        if s2.transport and s2.transport.ssps_unit and s2.transport.ssps_unit.owner:
            owner_name = s2.transport.ssps_unit.owner.name
        line(f"Предприятие-владелец: {owner_name}")
        line(f"Тип машины: {s2.machine_type.name if s2.machine_type else '—'}")
        line(f"Номер: {s2.transport.number if s2.transport else '—'}")
        line(f"Спидометр: {v(s2.speedometer_out_km)} / {v(s2.speedometer_in_km)}")
        line(f"Моточасы: {v(s2.moto_hours_out)} / {v(s2.moto_hours_in)}")
        line(
					f"Топливо: {v(s2.fuel_type)} | Выдано: {v(s2.fuel_issued_l)} | "
          f"Ост. выезд: {v(s2.fuel_left_out_l)} | Ост. возврат: {v(s2.fuel_left_in_l)}"
				)
    else:
        line("Раздел II не заполнен.")

    ensure_space(150)
    line("Раздел III. Сведения о работе единицы ССПС", dy=14, bold=True)
    for idx, w in enumerate(rs.work_rows.all(), start=1):
        line(
            f"{idx}. № {v(w.request_no)} | {v(w.station_from)} → {v(w.station_to)} | "
            f"{v(w.time_departure)}-{v(w.time_arrival)} | Работы: {v(w.work_name)} | Место: {v(w.work_place)}"
        )

    ensure_space(140)

    s4 = getattr(rs, "section_iv", None)
    s5 = getattr(rs, "section_v", None)
    s6 = getattr(rs, "section_vi", None)

    line("Раздел IV — результаты работы и расход ТСМ", dy=14, bold=True)
    line(f"Состояние: {v(s4.technical_state) if s4 else '—'}")
    line(f"Неисправности: {v(s4.defects_found) if s4 else '—'}")
    line(f"Меры: {v(s4.measures_taken) if s4 else '—'}")

    line("Раздел V — Тех. состояние и допуски", dy=14, bold=True)
    line(f"Допуски/примечания: {v(s5.fuel_notes) if s5 else '—'}")
    line(f"Связь/устройства: {v(s5.repairs_notes) if s5 else '—'}")
    line(f"Ответственный: {v(s5.master_name) if s5 else '—'}")

    line("VI. Замечания машиниста-инструктора/ревизора", dy=14, bold=True)
    line(f"Замечания: {v(s6.final_notes) if s6 else '—'}")
    line(f"Проверил: {v(s6.inspector_name) if s6 else '—'}")
    
    ensure_space(80)
    med = getattr(rs, "medical", None)
    line("Медосмотр", dy=14, bold=True)
    if med:
        line(f"До: {v(med.pre_time)} | Допуск: {'ДА' if med.pre_allowed else 'НЕТ'} | Медик: {v(med.pre_medic_name)}")
        line(f"После: {v(med.post_time)} | Допуск: {'ДА' if med.post_allowed else 'НЕТ'} | Медик: {v(med.post_medic_name)}")
    else:
        line("Нет данных медосмотра.")

    c.showPage()
    c.save()
    return buf.getvalue()