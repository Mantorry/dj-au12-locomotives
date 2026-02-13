from ..models import RouteSheetAU12, AU12CrewRow


def prefill_crew_from_brigade(rs: RouteSheetAU12) -> None:
    if not rs.brigade_id:
        return
    if rs.crew_rows.exists():
        return

    members = rs.brigade.members.all().order_by("last_name", "first_name", "patronymic", "username")[:12]
    for m in members:
        fio = " ".join([m.last_name or "", m.first_name or "", getattr(m, "patronymic", "") or ""]).strip()
        AU12CrewRow.objects.create(
            routesheet=rs,
            position_text=getattr(m, "get_role_display", lambda: "")(),
            full_name=fio or m.username,
        )
