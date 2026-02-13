from apps.accounts.models import Role
from ..models import RouteSheetAU12, AU12Status, AU12Step


def can_access_step(user, rs: RouteSheetAU12, target_step: str) -> bool:
    if getattr(user, "is_superuser", False) or getattr(user, "role", None) == Role.ADMIN:
        return True

    role = getattr(user, "role", None)

    if target_step == AU12Step.MED_PRE:
        return role == Role.MEDIC

    if target_step == AU12Step.MASTER_ISSUE:
        return role == Role.MASTER and rs.is_med_pre_done()

    if target_step == AU12Step.CREW_WORK:
        return role in {Role.MACHINIST, Role.ASSISTANT, Role.MASTER} and rs.step in {
            AU12Step.MASTER_ISSUE, AU12Step.CREW_WORK
        }

    if target_step == AU12Step.MED_POST:
        # медик после работы — только когда I–VI заполнены
        return role == Role.MEDIC and (
            rs.is_section_i_done()
            and rs.is_section_ii_done()
            and rs.is_section_iii_done()
            and rs.is_section_iv_done()
            and rs.is_section_v_done()
            and rs.is_section_vi_done()
        )

    if target_step == AU12Step.FINAL_REVIEW:
        return role in {Role.MASTER, Role.INSPECTOR} and rs.is_fully_done()

    return False


def recalc_status_and_step(rs: RouteSheetAU12) -> None:
    if rs.status == AU12Status.COMPLETED:
        return

    if not rs.is_med_pre_done():
        rs.step = AU12Step.MED_PRE
        rs.status = AU12Status.DRAFT
        return

    if rs.step == AU12Step.MED_PRE:
        rs.step = AU12Step.MASTER_ISSUE
        rs.status = AU12Status.DRAFT
        return

    if rs.step == AU12Step.MASTER_ISSUE:
        rs.status = AU12Status.DRAFT
        return

    # при работе бригады
    if rs.step == AU12Step.CREW_WORK:
        if rs.is_section_i_done() or rs.is_section_ii_done() or rs.is_section_iii_done() or rs.is_section_iv_done() or rs.is_section_v_done() or rs.is_section_vi_done():
            rs.status = AU12Status.IN_PROGRESS
        else:
            rs.status = AU12Status.ISSUED

        if rs.is_fully_done():
            rs.status = AU12Status.READY
            rs.step = AU12Step.FINAL_REVIEW
        return

    if rs.is_fully_done():
        rs.status = AU12Status.READY
        rs.step = AU12Step.FINAL_REVIEW


def mark_issued_by_master(rs: RouteSheetAU12) -> None:
    rs.step = AU12Step.CREW_WORK
    rs.status = AU12Status.ISSUED


def finalize_routesheet(rs: RouteSheetAU12) -> None:
    rs.status = AU12Status.COMPLETED
    rs.step = AU12Step.FINAL_REVIEW
