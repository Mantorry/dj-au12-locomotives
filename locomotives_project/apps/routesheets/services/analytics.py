from decimal import Decimal
from ..models import RouteSheetAU12


def run_km(rs: RouteSheetAU12) -> int:
    s2 = getattr(rs, "section_ii", None)
    if not s2 or s2.speedometer_out_km is None or s2.speedometer_in_km is None:
        return 0
    return max(0, int(s2.speedometer_in_km) - int(s2.speedometer_out_km))


def fuel_consumed_l(rs: RouteSheetAU12) -> Decimal:
    s2 = getattr(rs, "section_ii", None)
    if not s2:
        return Decimal("0")
    return (Decimal(s2.fuel_left_out_l) + Decimal(s2.fuel_issued_l) - Decimal(s2.fuel_left_in_l))


def consumption_l_per_100km(rs: RouteSheetAU12) -> float:
    km = run_km(rs)
    if km <= 0:
        return 0.0
    fuel = float(fuel_consumed_l(rs))
    return (fuel / km) * 100.0
