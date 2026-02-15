from ..models import RouteSheetAU12, AU12SectionII
from apps.directory.models import MachineType, TransportUnit

def _find_transport_for_ssps(rs: RouteSheetAU12):
    qs = TransportUnit.objects.filter(is_active=True).select_related("machine_type")

    # 1) Жёсткая привязка транспорта к ССПС
    tr = qs.filter(ssps_unit=rs.ssps_unit).first()
    if tr:
        return tr

    # 2) Фолбэк: по номеру машины из ССПС
    tr = qs.filter(number=rs.ssps_unit.number).first()
    if tr:
        return tr

    return None

def _find_machine_type_for_ssps(rs: RouteSheetAU12):
    return MachineType.objects.filter(name__iexact=rs.ssps_unit.type_name).first()

def prefill_section_ii_from_previous(rs: RouteSheetAU12) -> None:
    # Раздел II
    s2, _ = AU12SectionII.objects.get_or_create(routesheet=rs)

    if not s2.transport_id:
        tr = _find_transport_for_ssps(rs)
        if tr:
            s2.transport = tr
            if not s2.machine_type_id:
              s2.machine_type = tr.machine_type

    # если транспорт есть, но тип не заполнен — дотягиваем тип
    if s2.transport_id and not s2.machine_type_id:
        s2.machine_type = s2.transport.machine_type

    # если транспорт не найден, но тип ещё пуст — пробуем подобрать тип по наименованию ССПС
    if not s2.machine_type_id:
        mt = _find_machine_type_for_ssps(rs)
        if mt:
            s2.machine_type = mt

    s2.save()
