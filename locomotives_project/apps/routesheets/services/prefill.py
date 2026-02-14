from ..models import RouteSheetAU12, AU12SectionII
from apps.directory.models import TransportUnit

def prefill_section_ii_from_previous(rs: RouteSheetAU12) -> None:
    # Раздел II
    s2, _ = AU12SectionII.objects.get_or_create(routesheet=rs)

    # если транспорт не выбран — пробуем найти транспорт, привязанный к ССПС
    if not s2.transport_id:
        tr = (
            TransportUnit.objects
            .filter(is_active=True, ssps_unit=rs.ssps_unit)
            .select_related("machine_type")
            .first()
        )
        if tr:
            s2.transport = tr
            s2.machine_type = tr.machine_type

    # если транспорт есть, но тип не заполнен — дотягиваем тип
    if s2.transport_id and not s2.machine_type_id:
        s2.machine_type = s2.transport.machine_type

    s2.save()
