"""Extract the main-deck outline (half-breadth plan) from the decks drawing.

The MAIN DECK plan view is, geometrically, a table of half-breadths at deck
level. This finds the outer hull contour and reports beam/length as a RATIO,
which is scale-independent -- no need to know or trust the drawing's scale
bar. Multiplying by a known LOA then gives feet.

Caveat that governs everything downstream: this is USCGC Point Barnes, a
SISTER SHIP. It yields CLASS geometry, not Eris geometry. One physical
measurement aboard validates (or refutes) the transfer.

Run: python deck_outline.py --tif "<Decks.tif>" --loa-ft 82
"""
from __future__ import annotations

import argparse
import json

import cv2
import numpy as np

# Main deck plan occupies the upper portion of the sheet.
MAIN_DECK_BOX = (0.0, 0.02, 1.0, 0.44)   # x0, y0, x1, y1 as fractions


def extract(tif: str, box=MAIN_DECK_BOX):
    img = cv2.imread(tif, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise SystemExit(f"cannot read {tif}")
    H, W = img.shape
    x0, y0, x1, y1 = box
    reg = img[int(H * y0):int(H * y1), int(W * x0):int(W * x1)]

    _, bw = cv2.threshold(reg, 0, 255,
                          cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    # close small gaps so the hull outline is a single connected curve
    bw = cv2.morphologyEx(
        bw, cv2.MORPH_CLOSE,
        cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)))

    cnts, _ = cv2.findContours(bw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if not cnts:
        raise SystemExit("no contours found")
    hull = max(cnts, key=cv2.contourArea)
    return reg, hull


def halfbreadths(hull: np.ndarray, n_stations: int = 21,
                 min_width_px: int = 100):
    """Sample the contour: for each x, the min and max y of the outline.

    min_width_px trims dimension lines and leaders that the contour picks up
    beyond the hull ends. Those artifacts are only a line-thickness wide, so
    any x whose extent is under ~100 px (about 1 ft) is not hull. Found the
    hard way: the first run reported the stern half-breadth as 0.12 ft, which
    is impossible for a transom, because a dimension arrow ran off the stern.
    The width profile confirms the split cleanly -- 24 px at x=0, then 752 px
    (7.4 ft) by x=50 where the real transom begins. Cost: the last ~0.5 ft of
    the bow point is trimmed too, which shortens length slightly and so
    biases the derived beam marginally HIGH.
    """
    pts = hull.reshape(-1, 2)
    xs, ys = pts[:, 0], pts[:, 1]
    # width profile over the full x-range, to locate the true hull extent
    x_lo, x_hi = int(xs.min()), int(xs.max())
    widths_all = {}
    for x in range(x_lo, x_hi + 1, 5):
        m = np.abs(xs - x) <= 2
        if m.sum() >= 2:
            widths_all[x] = int(ys[m].max() - ys[m].min())
    hull_xs = [x for x, w in widths_all.items() if w >= min_width_px]
    if not hull_xs:
        raise SystemExit("no hull-width columns found")
    x_min, x_max = min(hull_xs), max(hull_xs)
    length_px = x_max - x_min
    rows = []
    for i in range(n_stations):
        x = x_min + round(length_px * i / (n_stations - 1))
        m = np.abs(xs - x) <= 2
        if m.sum() < 2:
            rows.append((i / (n_stations - 1), None, None))
            continue
        y_lo, y_hi = int(ys[m].min()), int(ys[m].max())
        rows.append((i / (n_stations - 1), y_hi - y_lo, (y_lo + y_hi) / 2))
    true_max = max(w for x, w in widths_all.items() if x_min <= x <= x_max)
    max_x = [x for x, w in widths_all.items()
             if w == true_max and x_min <= x <= x_max][0]
    return rows, length_px, true_max, (max_x - x_min) / length_px


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tif", required=True)
    ap.add_argument("--loa-ft", type=float, default=82.0,
                    help="known length overall, to convert the ratio to feet")
    ap.add_argument("--out", default="deck_offsets.json")
    a = ap.parse_args()

    reg, hull = extract(a.tif)
    rows, length_px, max_w_px, max_at = halfbreadths(hull)
    ratio = max_w_px / length_px
    beam_ft = ratio * a.loa_ft

    print(f"main-deck region : {reg.shape[1]}x{reg.shape[0]} px")
    print(f"outline length   : {length_px} px")
    print(f"outline max width: {max_w_px} px")
    print(f"\nbeam / length ratio = {ratio:.4f}   (scale-independent)")
    print(f"at LOA {a.loa_ft:.1f} ft  ->  BEAM = {beam_ft:.2f} ft "
          f"({int(beam_ft)} ft {round((beam_ft % 1) * 12)} in)")
    print(f"max beam occurs {100*max_at:.0f}% of the length forward of the "
          f"transom")

    px_per_ft = length_px / a.loa_ft
    print(f"\nimplied scale    : {px_per_ft:.1f} px/ft")
    print("\nhalf-breadths at deck (fraction aft of bow -> half-breadth ft):")
    for frac, w, _ in rows:
        if w:
            print(f"  {frac:5.2f}   {w / px_per_ft / 2:6.2f} ft")

    json.dump({
        "source": "USCGC Point Barnes (SISTER SHIP) main deck plan",
        "beam_length_ratio": round(ratio, 5),
        "assumed_loa_ft": a.loa_ft,
        "derived_beam_ft": round(beam_ft, 2),
        "max_beam_at_frac_from_stern": round(max_at, 3),
        "px_per_ft": round(px_per_ft, 2),
        "half_breadths_ft": [
            {"frac_from_bow": round(f, 3),
             "half_breadth_ft": round(w / px_per_ft / 2, 2) if w else None}
            for f, w, _ in rows],
        "WARNING": "class geometry from a sister ship; validate against one "
                   "physical beam measurement aboard Eris before use.",
    }, open(a.out, "w", encoding="utf-8"), indent=1)
    print(f"\nwrote {a.out}")

    vis = cv2.cvtColor(reg, cv2.COLOR_GRAY2BGR)
    cv2.drawContours(vis, [hull], -1, (0, 0, 255), 3)
    cv2.imwrite("deck_outline_overlay.png",
                cv2.resize(vis, (vis.shape[1] // 3, vis.shape[0] // 3)))
    print("wrote deck_outline_overlay.png")


if __name__ == "__main__":
    main()
