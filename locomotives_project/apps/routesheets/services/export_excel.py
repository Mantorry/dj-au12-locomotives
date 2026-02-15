from io import BytesIO

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Side, Font
from openpyxl.utils import get_column_letter


def export_au12_excel(rs) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = "АУ-12"

    thin = Side(style="thin")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    def v(val):
        return val if val not in [None, ""] else "-"

    def cell(r, c, v="", bold=False, wrap=True, align="left"):
        ce = ws.cell(row=r, column=c, value=v)
        ce.font = Font(bold=bold)
        ce.alignment = Alignment(horizontal=align, vertical="top", wrap_text=wrap)
        ce.border = border
        return ce

    # ширины
    widths = [8, 18, 35, 12, 12, 10, 10]
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w

    # заголовок
    ws.merge_cells("A1:K1")
    cell(1, 1, "МАРШРУТНЫЙ ЛИСТ формы АУ-12", bold=True, align="center")
    ws.merge_cells("A2:K2")
    cell(2, 1, f"№ {rs.number} от {rs.date}", bold=True, align="center")

    ws.merge_cells("B3:K3"); cell(3, 1, "Дорога", bold=True); cell(3, 2, v(rs.railway_name))
    ws.merge_cells("B4:K4"); cell(4, 1, "Предприятие", bold=True); cell(4, 2, rs.enterprise.name if rs.enterprise else "—")
    ws.merge_cells("B5:K5"); cell(5, 1, "ССПС", bold=True); cell(5, 2, str(rs.ssps_unit))
    ws.merge_cells("B6:K6"); cell(6, 1, "Бригада", bold=True); cell(6, 2, rs.brigade.name if rs.brigade else "—")

    # Раздел I
    r = 8
    ws.merge_cells(f"A{r}:K{r}"); cell(r, 1, "I. Бригада", bold=True); r += 1
    headers = ["№", "Должность", "ФИО", "Явка", "Оконч.", "Перер.", "Отдых"]
    for col, h in enumerate(headers, start=1):
        cell(9, col, h, bold=True, align="center")

    r = 10
    for idx, row in enumerate(rs.crew_rows.all(), start=1):
        cell(r, 1, idx, align="center")
        cell(r, 2, row.position_display)
        ws.merge_cells(f"C{r}:D{r}"); cell(r, 3, row.full_name)
        cell(r, 5, str(row.time_check_in or ""), align="center")
        cell(r, 6, str(row.time_check_out or ""), align="center")
        cell(r, 7, row.overtime_minutes, align="center")
        cell(r, 8, row.rest_minutes, align="center")
        r += 1


    # Раздел II
    
    s2 = getattr(rs, "section_ii", None)

    r += 1
    ws.merge_cells(f"A{r}:K{r}"); cell(r, 1, "II. Пробег, моточасы, ТСМ", bold=True); r += 1
    cell(r, 1, "Тип машины", bold=True); ws.merge_cells(f"B{r}:D{r}"); cell(r, 2, s2.machine_type.name if s2 and s2.machine_type else "—")
    cell(r, 5, "Номер", bold=True); ws.merge_cells(f"F{r}:H{r}"); cell(r, 6, s2.transport.number if s2 and s2.transport else "—"); r += 1
    cell(r, 1, "Спидометр выезд", bold=True); cell(r, 2, v(s2.speedometer_out_km) if s2 else "—")
    cell(r, 3, "Спидометр возврат", bold=True); cell(r, 4, v(s2.speedometer_in_km) if s2 else "—")
    cell(r, 5, "Моточасы выезд", bold=True); cell(r, 6, v(s2.moto_hours_out) if s2 else "—")
    cell(r, 7, "Моточасы возврат", bold=True); cell(r, 8, v(s2.moto_hours_in) if s2 else "—"); r += 1
    cell(r, 1, "Топливо", bold=True); cell(r, 2, v(s2.fuel_type) if s2 else "—")
    cell(r, 3, "Выдано", bold=True); cell(r, 4, v(s2.fuel_issued_l) if s2 else "—")
    cell(r, 5, "Ост. выезд", bold=True); cell(r, 6, v(s2.fuel_left_out_l) if s2 else "—")
    cell(r, 7, "Ост. возврат", bold=True); cell(r, 8, v(s2.fuel_left_in_l) if s2 else "—")

    r += 2

    # Раздел III
    ws.merge_cells(f"A{r}:K{r}"); cell(r, 1, "III. Сведения о работе единицы ССПС", bold=True); r += 1
    headers3 = ["№ заявки", "Станция от", "Станция до", "Отпр.", "Приб.", "Наим. работы", "Место", "Начало", "Оконч.", "Объем", "Подпись"]
    for col, h in enumerate(headers3, 1):
        cell(r, col, h, bold=True, align="center")
    r += 1

    for w in rs.work_rows.all()[:12]:
        cell(r, 1, w.request_no)
        cell(r, 2, str(w.station_from or ""))
        cell(r, 3, str(w.station_to or ""))
        cell(r, 4, str(w.time_departure or ""), align="center")
        cell(r, 5, str(w.time_arrival or ""), align="center")
        cell(r, 6, w.work_name)
        cell(r, 7, w.work_place)
        cell(r, 8, str(w.machine_work_start or ""), align="center")
        cell(r, 9, str(w.machine_work_end or ""), align="center")
        cell(r, 10, w.work_volume)
        cell(r, 11, w.supervisor_signature)
        r += 1

    r += 1

    # Разделы IV–VI
    s4 = getattr(rs, "section_iv", None)
    s5 = getattr(rs, "section_v", None)
    s6 = getattr(rs, "section_vi", None)

    r += 1
    ws.merge_cells(f"A{r}:K{r}"); cell(r, 1, "IV. Результаты работы и расход ТСМ", bold=True); r += 1
    ws.merge_cells(f"A{r}:K{r}"); cell(r, 1, f"Состояние: {v(s4.technical_state) if s4 else '—'}"); r += 1
    ws.merge_cells(f"A{r}:K{r}"); cell(r, 1, f"Неисправности: {v(s4.defects_found) if s4 else '—'}"); r += 1
    ws.merge_cells(f"A{r}:K{r}"); cell(r, 1, f"Принятые меры: {v(s4.measures_taken) if s4 else '—'}"); r += 2
    ws.merge_cells(f"A{r}:G{r}"); cell(r, 1, "Раздел V", bold=True); r += 1
    ws.merge_cells(f"A{r}:G{r}"); cell(r, 1, (s5.fuel_notes if s5 else ""), wrap=True); ws.row_dimensions[r].height = 45; r += 2

    ws.merge_cells(f"A{r}:K{r}"); cell(r, 1, "V. Техническое состояние и допуски", bold=True); r += 1
    ws.merge_cells(f"A{r}:K{r}"); cell(r, 1, f"Допуски/примечания: {v(s5.fuel_notes) if s5 else '—'}"); r += 1
    ws.merge_cells(f"A{r}:K{r}"); cell(r, 1, f"Связь/устройства: {v(s5.repairs_notes) if s5 else '—'}"); r += 2
    
    out = BytesIO()
    wb.save(out)
    return out.getvalue()
