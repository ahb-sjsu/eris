"""Where does Eris actually operate, and do stern lift devices apply there?

Trim tabs and interceptors are dynamic-lift devices. Whether they help is
not a matter of opinion; it depends on the speed regime, which is set by
Froude number. This computes it.

Run: python trim_regime.py
"""
from __future__ import annotations

G = 9.80665
KT_TO_MS = 0.514444
FT_TO_M = 0.3048

LWL_FT = 78.0          # estimate; hull digitization settles it
CRUISE_KT = 9.6        # owner-reported
FULL_KT = 14.0         # class max, approximate -- verify


def froude(v_kts: float, lwl_ft: float) -> float:
    return (v_kts * KT_TO_MS) / (G * lwl_ft * FT_TO_M) ** 0.5


def speed_length(v_kts: float, lwl_ft: float) -> float:
    return v_kts / lwl_ft ** 0.5


REGIMES = [
    (0.00, 0.30, "displacement", "hull is fully supported by buoyancy; "
     "dynamic lift is negligible"),
    (0.30, 0.40, "upper displacement", "wavemaking rising steeply; running "
     "trim still essentially static"),
    (0.40, 0.70, "semi-displacement", "dynamic lift begins to matter; stern "
     "lift devices start to pay"),
    (0.70, 1.10, "semi-planing", "significant bow-up trim; tabs/interceptors "
     "clearly effective"),
    (1.10, 9.99, "planing", "trim control is essential"),
]


def regime(fn: float) -> tuple[str, str]:
    for lo, hi, name, note in REGIMES:
        if lo <= fn < hi:
            return name, note
    return "?", ""


def main() -> None:
    print(f"Eris, LWL {LWL_FT:.0f} ft (estimate)\n" + "=" * 62)
    for label, v in (("cruise", CRUISE_KT), ("max (approx)", FULL_KT)):
        fn = froude(v, LWL_FT)
        sl = speed_length(v, LWL_FT)
        name, note = regime(fn)
        print(f"\n{label:14s} {v:4.1f} kt")
        print(f"  Froude number      Fn = {fn:.3f}")
        print(f"  speed/length ratio S/L = {sl:.2f}")
        print(f"  regime             {name}")
        print(f"                     {note}")

    print("\n" + "=" * 62)
    fn_c = froude(CRUISE_KT, LWL_FT)
    print("Threshold where stern lift devices begin to earn their drag:")
    for lo, _, name, _ in REGIMES:
        if name == "semi-displacement":
            v_thresh = lo * (G * LWL_FT * FT_TO_M) ** 0.5 / KT_TO_MS
            print(f"  Fn >= {lo:.2f}  ->  {v_thresh:.1f} kt on this LWL")
            print(f"  Eris cruises at {CRUISE_KT} kt (Fn {fn_c:.3f}), i.e. "
                  f"{100*fn_c/lo:.0f}% of that threshold.")
            break


if __name__ == "__main__":
    main()
