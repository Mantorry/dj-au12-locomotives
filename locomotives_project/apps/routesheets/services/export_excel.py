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

    def cell(r, c, v="", bold=False, wrap=True, align="left"):
        ce = ws.cell(row=r, column=c, value=v)
        ce.font = Font(bold=bold)
        ce.alignment = Alignment(horizontal=align, vertical="top", wrap_text=wrap)
        ce.border = border
        return ce

    # ширины
    widths = [6, 18, 35, 12, 12, 10, 10]
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w

    # заголовок
    ws.merge_cells("A1:G1")
    cell(1, 1, "МАРШРУТНЫЙ ЛИСТ формы АУ-12", bold=True, align="center")
    ws.merge_cells("A2:G2")
    cell(2, 1, f"№ {rs.number} от {rs.date}", bold=True, align="center")

    cell(3, 1, "Дорога:", bold=True); ws.merge_cells("B3:G3"); cell(3, 2, rs.railway_name or "—")
    cell(4, 1, "Предприятие:", bold=True); ws.merge_cells("B4:G4"); cell(4, 2, rs.enterprise_name or "—")
    cell(5, 1, "ССПС:", bold=True); ws.merge_cells("B5:G5"); cell(5, 2, str(rs.ssps_unit))
    cell(6, 1, "Бригада:", bold=True); ws.merge_cells("B6:G6"); cell(6, 2, rs.brigade.name if rs.brigade else "—")

    # Раздел I
    ws.merge_cells("A8:G8"); cell(8, 1, "Раздел I. Бригада", bold=True, align="left")
    headers = ["№", "Должность", "ФИО", "Явка", "Оконч.", "Перер.", "Отдых"]
    for col, h in enumerate(headers, start=1):
        cell(9, col, h, bold=True, align="center")

    r = 10
    for idx, row in enumerate(rs.crew_rows.all(), start=1):
        cell(r, 1, idx, align="center")
        cell(r, 2, row.position_display)
        cell(r, 3, row.full_name)
        cell(r, 4, str(row.time_check_in or ""))
        cell(r, 5, str(row.time_check_out or ""))
        cell(r, 6, row.overtime_minutes, align="center")
        cell(r, 7, row.rest_minutes, align="center")
        r += 1
        if r > 18:
            break

    r += 1

    # Раздел II
    ws.merge_cells(f"A{r}:G{r}"); cell(r, 1, "Раздел II. Пробег, моточасы, ТСМ", bold=True); r += 1
    s2 = getattr(rs, "section_ii", None)

    def vv(v):
        return v if v not in [None, ""] else "—"

    cell(r, 1, "Предприятие-владелец", bold=True); ws.merge_cells(f"B{r}:G{r}")
    cell(r, 2, vv(s2.enterprise_owner_display) if s2 else "—"); r += 1

    cell(r, 1, "Тип машины", bold=True); ws.merge_cells(f"B{r}:D{r}")
    cell(r, 2, vv(s2.machine_type_display) if s2 else "—")
    cell(r, 5, "Номер", bold=True); ws.merge_cells(f"F{r}:G{r}")
    cell(r, 6, vv(s2.machine_number) if s2 else "—")
    r += 1

    cell(r, 1, "Спидометр выезд", bold=True); cell(r, 2, vv(s2.speedometer_out_km) if s2 else "—")
    cell(r, 3, "Спидометр возврат", bold=True); cell(r, 4, vv(s2.speedometer_in_km) if s2 else "—")
    cell(r, 5, "Моточасы выезд", bold=True); cell(r, 6, vv(s2.moto_hours_out) if s2 else "—")
    cell(r, 7, vv(s2.moto_hours_in) if s2 else "—")
    r += 2

    # Раздел III
    ws.merge_cells(f"A{r}:G{r}"); cell(r, 1, "Раздел III. Работы", bold=True); r += 1
    headers3 = ["№", "Станция от", "Станция до", "Отпр.", "Приб.", "Работы", "Место"]
    for col, h in enumerate(headers3, start=1):
        cell(r, col, h, bold=True, align="center")
    r += 1

    for w in rs.work_rows.all()[:8]:
        cell(r, 1, w.request_no)
        cell(r, 2, str(w.station_from or ""))
        cell(r, 3, str(w.station_to or ""))
        cell(r, 4, str(w.time_departure or ""))
        cell(r, 5, str(w.time_arrival or ""))
        cell(r, 6, w.work_display)
        cell(r, 7, w.work_place_display)
        r += 1

    r += 1

    # Разделы IV–VI
    s4 = getattr(rs, "section_iv", None)
    s5 = getattr(rs, "section_v", None)
    s6 = getattr(rs, "section_vi", None)

    ws.merge_cells(f"A{r}:G{r}"); cell(r, 1, "Раздел IV", bold=True); r += 1
    ws.merge_cells(f"A{r}:G{r}"); cell(r, 1, (s4.technical_state if s4 else ""), wrap=True); ws.row_dimensions[r].height = 45; r += 2

    ws.merge_cells(f"A{r}:G{r}"); cell(r, 1, "Раздел V", bold=True); r += 1
    ws.merge_cells(f"A{r}:G{r}"); cell(r, 1, (s5.fuel_notes if s5 else ""), wrap=True); ws.row_dimensions[r].height = 45; r += 2

    ws.merge_cells(f"A{r}:G{r}"); cell(r, 1, "Раздел VI", bold=True); r += 1
    ws.merge_cells(f"A{r}:G{r}"); cell(r, 1, (s6.final_notes if s6 else ""), wrap=True); ws.row_dimensions[r].height = 55

    bio = BytesIO()
    wb.save(bio)
    return bio.getvalue()
