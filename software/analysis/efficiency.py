"""Transport-efficiency metrics for Eris at the owner-reported cruise point.

Reproducible so the numbers can be re-run when the hull digitization gives a
measured displacement and LWL, and when the twin's fuel-flow channels give a
burn curve instead of a single point.

Run: python efficiency.py
"""
from __future__ import annotations

# --- owner-reported, schema/points.yaml performance.cruise -----------------
SPEED_KTS = 9.6
BURN_GPH = 14.0          # both mains + house load
FUEL_GAL = 2026.0        # 2x920 wing + 186 day

# --- class/estimated figures: REPLACE at hull digitization -----------------
LWL_FT = 78.0            # estimate; lines plan settles it
DISPL_LT = 69.0          # class full-load estimate, long tons
HOUSE_LOAD_GPH = 4.0     # estimate of the non-propulsion share of the 14

# --- diesel constants ------------------------------------------------------
BSFC_LB_PER_HP_HR = 0.38   # marine diesel, moderate load
DIESEL_LB_PER_GAL = 7.1


def hull_speed_kts(lwl_ft: float) -> float:
    return 1.34 * lwl_ft ** 0.5


def speed_length_ratio(v_kts: float, lwl_ft: float) -> float:
    return v_kts / lwl_ft ** 0.5


def shp_from_burn(gph: float) -> float:
    """Shaft horsepower implied by a fuel rate, at assumed BSFC."""
    return gph * DIESEL_LB_PER_GAL / BSFC_LB_PER_HP_HR


def report() -> dict:
    nm_per_gal = SPEED_KTS / BURN_GPH
    gal_per_nm = 1 / nm_per_gal
    endurance_h = FUEL_GAL / BURN_GPH
    range_nm = endurance_h * SPEED_KTS
    hs = hull_speed_kts(LWL_FT)
    sl = speed_length_ratio(SPEED_KTS, LWL_FT)
    prop_gph = BURN_GPH - HOUSE_LOAD_GPH
    prop_hp_total = shp_from_burn(prop_gph)

    out = {
        "nm_per_gal": nm_per_gal,
        "gal_per_nm": gal_per_nm,
        "gal_per_nm_per_LT": gal_per_nm / DISPL_LT,
        "ton_miles_per_gal": DISPL_LT * nm_per_gal,
        "endurance_h": endurance_h,
        "range_nm_no_reserve": range_nm,
        "range_nm_10pct_reserve": range_nm * 0.9,
        "hull_speed_kts": hs,
        "pct_of_hull_speed": 100 * SPEED_KTS / hs,
        "speed_length_ratio": sl,
        "propulsion_hp_total_est": prop_hp_total,
        "propulsion_hp_per_engine_est": prop_hp_total / 2,
    }

    print(f"Eris at {SPEED_KTS} kt / {BURN_GPH} gph combined\n" + "=" * 46)
    print(f"  transport efficiency   {nm_per_gal:.3f} nm/gal "
          f"({gal_per_nm:.2f} gal/nm)")
    print(f"  ton-miles per gallon   {out['ton_miles_per_gal']:.1f} "
          f"(at {DISPL_LT:.0f} LT est.)")
    print(f"  fuel per ton-mile      {out['gal_per_nm_per_LT']:.4f} gal/(nm*LT)")
    print(f"  endurance              {endurance_h:.0f} h")
    print(f"  range                  {range_nm:.0f} nm no reserve, "
          f"{out['range_nm_10pct_reserve']:.0f} nm at 10%")
    print(f"\n  hull speed (LWL {LWL_FT:.0f} ft)  {hs:.1f} kt")
    print(f"  cruising at            {out['pct_of_hull_speed']:.0f}% of hull "
          f"speed, S/L = {sl:.2f}")
    print(f"\n  propulsion power est.  {prop_hp_total:.0f} hp total, "
          f"{out['propulsion_hp_per_engine_est']:.0f} hp/engine")
    print(f"    (assumes {HOUSE_LOAD_GPH:.0f} gph house load, BSFC "
          f"{BSFC_LB_PER_HP_HR})")
    return out


if __name__ == "__main__":
    report()
