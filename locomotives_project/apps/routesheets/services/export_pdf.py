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
        c.drawString(x0, y0, text)
        y0 -= dy

    def ensure_space(h):
        nonlocal y0
        if y0 - h < 30:
            c.setFont("DejaVuSans", 9)
            y0 = height - 32

    line("МАРШРУТНЫЙ ЛИСТ формы АУ-12", dy=16, bold=True)
    line(f"№ {rs.number} от {rs.date}", dy=16)
    line(f"Дорога: {rs.railway_name}")
    line(f"Предприятие: {rs.enterprise_name if rs.enterprise else '—'}")
    line(f"ССПС: {rs.ssps_unit}")
    line(f"Бригада: {rs.brigade.name if rs.brigade else '—'}", dy=16)

    # Раздел I
    line("I. Бригада", bold=True)
    for idx, r in enumerate(rs.crew_rows.all()[:12], start=1):
        line(
            f"{idx}. {v(r.position_display)} | {v(r.full_name)} | явка {v(r.time_check_in)} | оконч. {v(r.time_check_out)} | перер. {v(r.overtime_minutes)} | отдых {v(r.rest_minutes)}"
        )
        
    ensure_space(120)
    # Раздел II
    line("II. Пробег, моточасы, ТСМ", dy=14, bold=True)
    s2 = getattr(rs, "section_ii", None)
    if s2:
        line(
            f"Тип машины: {s2.machine_type.name if s2.machine_type else '—'} | Номер: {s2.transport.number if s2.transport else '—'}"
        )
        line(f"Спидометр: выезд {v(s2.speedometer_out_km)} / возврат {v(s2.speedometer_in_km)}")
        line(f"Моточасы: выезд {v(s2.moto_hours_out)} / возврат {v(s2.moto_hours_in)}")
        line(
            f"Топливо: {v(s2.fuel_type)} | выдано {v(s2.fuel_issued_l)} | ост. выезд {v(s2.fuel_left_out_l)} | ост. возврат {v(s2.fuel_left_in_l)}"
        )
        line(f"Смазка: {v(s2.lubricant_type)} | выдано {v(s2.lubricant_issued)}")
    else:
        line("Раздел II не заполнен.")

    ensure_space(150)
    line("III. Сведения о работе единицы ССПС", dy=14, bold=True)
    for idx, w in enumerate(rs.work_rows.all()[:10], start=1):
        line(
            f"{idx}. заявка {v(w.request_no)} | {v(w.station_from)} → {v(w.station_to)} | {v(w.time_departure)}-{v(w.time_arrival)} | {v(w.work_name)} | {v(w.work_place)} | маш. {v(w.machine_work_start)}-{v(w.machine_work_end)} | объем {v(w.work_volume)}"
        )

    ensure_space(140)
    # Раздел IV–VI текстом-блоками
    s4 = getattr(rs, "section_iv", None)
    s5 = getattr(rs, "section_v", None)
    s6 = getattr(rs, "section_vi", None)

    line("IV. Результаты работы и расход ТСМ", dy=14, bold=True)
    line(f"Состояние/замечания: {v(s4.technical_state) if s4 else '—'}")
    line(f"Неисправности: {v(s4.defects_found) if s4 else '—'}")
    line(f"Принятые меры: {v(s4.measures_taken) if s4 else '—'}")

    line("V. Техническое состояние и допуски", dy=14, bold=True)
    line(f"Допуски/примечания: {v(s5.fuel_notes) if s5 else '—'}")
    line(f"Связь/устройства: {v(s5.repairs_notes) if s5 else '—'}")
    line(f"Ответственный: {v(s5.master_name) if s5 else '—'} / Подпись: {v(s5.master_signature) if s5 else '—'}")

    line("VI. Замечания машиниста-инструктора/ревизора", dy=14, bold=True)
    line(f"Замечания: {v(s6.final_notes) if s6 else '—'}")
    line(f"Проверил: {v(s6.inspector_name) if s6 else '—'} / Подпись: {v(s6.inspector_signature) if s6 else '—'}")

    c.showPage()
    c.save()
    return buf.getvalue()