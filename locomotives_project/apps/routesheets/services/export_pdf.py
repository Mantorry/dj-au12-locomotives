import io
from decimal import Decimal

from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


def _reg_fonts():
    # Ожидаем, что шрифт лежит в static/fonts/
    # static/fonts/DejaVuSans.ttf
    font_path = settings.BASE_DIR / "static" / "fonts" / "DejaVuSans.ttf"
    pdfmetrics.registerFont(TTFont("DejaVuSans", str(font_path)))


def export_au12_pdf(rs) -> bytes:
    _reg_fonts()
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    c.setFont("DejaVuSans", 10)

    width, height = A4
    x0, y0 = 35, height - 40

    def line(text, dy=14, bold=False):
        nonlocal y0
        c.setFont("DejaVuSans", 10 if not bold else 11)
        c.drawString(x0, y0, text)
        y0 -= dy

    def box(x, y, w, h, title=None):
        c.rect(x, y - h, w, h, stroke=1, fill=0)
        if title:
            c.setFont("DejaVuSans", 9)
            c.drawString(x + 4, y - 12, title)

    line("МАРШРУТНЫЙ ЛИСТ формы АУ-12", dy=18, bold=True)
    line(f"№ {rs.number} от {rs.date}", dy=18)

    line(f"Дорога: {rs.railway_name or '—'}")
    line(f"Предприятие: {rs.enterprise_name or '—'}")
    line(f"ССПС: {rs.ssps_unit}")
    line(f"Бригада: {rs.brigade.name if rs.brigade else '—'}", dy=18)

    # Раздел I
    line("Раздел I. Бригада", dy=16, bold=True)
    y_table = y0
    box(x0, y_table, width - 2 * x0, 170)

    c.setFont("DejaVuSans", 8)
    c.drawString(x0 + 6, y_table - 22, "Должность")
    c.drawString(x0 + 120, y_table - 22, "ФИО")
    c.drawString(x0 + 360, y_table - 22, "Явка")
    c.drawString(x0 + 420, y_table - 22, "Оконч.")
    c.drawString(x0 + 485, y_table - 22, "Перер.")
    c.drawString(x0 + 535, y_table - 22, "Отдых")

    yy = y_table - 36
    for r in rs.crew_rows.all()[:8]:
        c.drawString(x0 + 6, yy, (r.position_display or "")[:18])
        c.drawString(x0 + 120, yy, (r.full_name or "")[:40])
        c.drawString(x0 + 360, yy, str(r.time_check_in or ""))
        c.drawString(x0 + 420, yy, str(r.time_check_out or ""))
        c.drawRightString(x0 + 520, yy, str(r.overtime_minutes or 0))
        c.drawRightString(x0 + 570, yy, str(r.rest_minutes or 0))
        yy -= 16

    y0 = y_table - 185

    # Раздел II
    line("Раздел II. Пробег, моточасы, ТСМ", dy=16, bold=True)
    y2 = y0
    box(x0, y2, width - 2 * x0, 140)

    s2 = getattr(rs, "section_ii", None)
    def v(val): return val if val not in [None, ""] else "—"
    if s2:
        c.setFont("DejaVuSans", 9)
        c.drawString(x0 + 6, y2 - 22, f"Предприятие-владелец: {v(s2.enterprise_owner_display)}")
        c.drawString(x0 + 6, y2 - 40, f"Тип машины: {v(s2.machine_type_display)}   Номер: {v(s2.machine_number)}")

        c.drawString(x0 + 6, y2 - 60, f"Спидометр: выезд {v(s2.speedometer_out_km)} / возврат {v(s2.speedometer_in_km)}")
        c.drawString(x0 + 6, y2 - 78, f"Моточасы: выезд {v(s2.moto_hours_out)} / возврат {v(s2.moto_hours_in)}")

        c.drawString(x0 + 6, y2 - 98, f"Топливо: {v(s2.fuel_type)}  Выдано: {v(s2.fuel_issued_l)}  Ост(выезд): {v(s2.fuel_left_out_l)}  Ост(возв): {v(s2.fuel_left_in_l)}")
        c.drawString(x0 + 6, y2 - 116, f"Смазка: {v(s2.lubricant_type)}  Выдано: {v(s2.lubricant_issued)}")
    else:
        c.setFont("DejaVuSans", 10)
        c.drawString(x0 + 6, y2 - 30, "Раздел II не заполнен.")

    y0 = y2 - 155

    # Раздел III (коротко)
    line("Раздел III. Работы", dy=16, bold=True)
    y3 = y0
    box(x0, y3, width - 2 * x0, 110)
    c.setFont("DejaVuSans", 8)
    c.drawString(x0 + 6, y3 - 22, "№ заявки")
    c.drawString(x0 + 70, y3 - 22, "Станция от")
    c.drawString(x0 + 170, y3 - 22, "Станция до")
    c.drawString(x0 + 270, y3 - 22, "Отпр.")
    c.drawString(x0 + 320, y3 - 22, "Приб.")
    c.drawString(x0 + 370, y3 - 22, "Работы/место")

    yy = y3 - 36
    for w in rs.work_rows.all()[:4]:
        c.drawString(x0 + 6, yy, (w.request_no or "")[:8])
        c.drawString(x0 + 70, yy, str(w.station_from or "")[:14])
        c.drawString(x0 + 170, yy, str(w.station_to or "")[:14])
        c.drawString(x0 + 270, yy, str(w.time_departure or ""))
        c.drawString(x0 + 320, yy, str(w.time_arrival or ""))
        c.drawString(x0 + 370, yy, f"{(w.work_display or '')[:14]} / {(w.work_place_display or '')[:14]}")
        yy -= 16

    y0 = y3 - 125

    # Раздел IV–VI текстом-блоками
    s4 = getattr(rs, "section_iv", None)
    s5 = getattr(rs, "section_v", None)
    s6 = getattr(rs, "section_vi", None)

    line("Раздел IV", dy=14, bold=True)
    box(x0, y0, width - 2 * x0, 55)
    c.setFont("DejaVuSans", 8)
    c.drawString(x0 + 6, y0 - 16, f"Замечания: {(s4.technical_state if s4 else '')[:110]}")
    c.drawString(x0 + 6, y0 - 30, f"Неисправности: {(s4.defects_found if s4 else '')[:110]}")
    c.drawString(x0 + 6, y0 - 44, f"Ответственный: {s4.responsible_name if s4 else ''}")
    y0 -= 70

    line("Раздел V", dy=14, bold=True)
    box(x0, y0, width - 2 * x0, 45)
    c.setFont("DejaVuSans", 8)
    c.drawString(x0 + 6, y0 - 16, f"ТСМ/примечания: {(s5.fuel_notes if s5 else '')[:120]}")
    c.drawString(x0 + 6, y0 - 30, f"Мастер: {s5.master_name if s5 else ''}")
    y0 -= 60

    line("Раздел VI", dy=14, bold=True)
    box(x0, y0, width - 2 * x0, 45)
    c.setFont("DejaVuSans", 8)
    c.drawString(x0 + 6, y0 - 16, f"Итог: {(s6.final_notes if s6 else '')[:120]}")
    c.drawString(x0 + 6, y0 - 30, f"Проверил: {s6.inspector_name if s6 else ''}")

    c.showPage()
    c.save()
    return buf.getvalue()
