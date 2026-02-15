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

def _get_or_create_machine_type_for_ssps(rs: RouteSheetAU12):
    """Возвращает существующий или создаёт тип машины по наименованию типа ССПС."""
    type_name = (rs.ssps_unit.type_name or "").strip()
    if not type_name:
        return None
    machine_type, _ = MachineType.objects.get_or_create(name=type_name)
    return machine_type


def _get_or_create_transport_for_ssps(rs: RouteSheetAU12, machine_type: MachineType | None):
    """
    Возвращает транспорт для ССПС.
    Если в справочнике транспорта записи ещё нет, создаёт её по данным ССПС
    (тип + номер), чтобы в разделе II сразу подставлялся "Номер машины".
    """
    if not machine_type:
        return None

    transport, _ = TransportUnit.objects.get_or_create(
        machine_type=machine_type,
        number=rs.ssps_unit.number,
        defaults={"ssps_unit": rs.ssps_unit, "is_active": True},
    )

    if transport.ssps_unit_id is None:
        transport.ssps_unit = rs.ssps_unit
        transport.save(update_fields=["ssps_unit"])

    return transport

def prefill_section_ii_from_previous(rs: RouteSheetAU12) -> None:
    # Раздел II
    s2, _ = AU12SectionII.objects.get_or_create(routesheet=rs)
    machine_type = s2.machine_type or _find_machine_type_for_ssps(rs) or _get_or_create_machine_type_for_ssps(rs)

    if not s2.transport_id:
        tr = _find_transport_for_ssps(rs)
        if not tr:
          tr = _get_or_create_transport_for_ssps(rs, machine_type)
        if tr:
            s2.transport = tr
            if not s2.machine_type_id:
                s2.machine_type = tr.machine_type

    # если транспорт есть, но тип не заполнен — дотягиваем тип
    if s2.transport_id and not s2.machine_type_id:
        s2.machine_type = s2.transport.machine_type

    # если транспорт не найден, но тип ещё пуст — пробуем подобрать тип по наименованию ССПС
    if not s2.machine_type_id:
        if machine_type:
          s2.machine_type = machine_type

    s2.save()
