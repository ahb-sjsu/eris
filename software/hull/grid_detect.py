"""Detect and calibrate the body-plan grid on the Point Barnes lines plan.

Step 1 of hull digitization. Fully automatable and independently checkable:
the waterline and buttock grid is drawn as long straight rules, so it can be
found by morphology rather than guessed. Calibration comes from the KNOWN
constant spacing of that grid, which turns pixels into feet.

Nothing here traces a station curve. That step needs human verification and
is deliberately separate -- a mis-read offset propagates silently into
displacement numbers that look plausible and are wrong.

Run: python grid_detect.py --tif "<path to Hull Lines.tif>"
"""
from __future__ import annotations

import argparse
import json
import os

import cv2
import numpy as np

# Body plan occupies the upper-middle of the sheet (fractions of full image).
BODY_PLAN_BOX = (0.33, 0.00, 0.62, 0.45)   # x0, y0, x1, y1


def load_region(tif: str, box=BODY_PLAN_BOX) -> np.ndarray:
    img = cv2.imread(tif, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise SystemExit(f"cannot read {tif}")
    H, W = img.shape
    x0, y0, x1, y1 = box
    return img[int(H * y0):int(H * y1), int(W * x0):int(W * x1)]


def binarize(gray: np.ndarray) -> np.ndarray:
    # Blueprint scans: ink is dark, paper light but stained. Otsu per-region.
    _, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    return bw


def find_rules(bw: np.ndarray, axis: str, min_frac: float = 0.15) -> list[int]:
    """Return positions of long straight rules along one axis.

    axis='h' finds horizontal rules (waterlines), 'v' finds vertical
    (buttocks/stations). A rule must span min_frac of the region to count,
    which rejects the curved section lines.
    """
    h, w = bw.shape
    if axis == "h":
        length = max(15, int(w * min_frac))
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (length, 1))
    else:
        length = max(15, int(h * min_frac))
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, length))
    lines = cv2.morphologyEx(bw, cv2.MORPH_OPEN, kernel)
    profile = lines.sum(axis=1 if axis == "h" else 0) / 255.0
    thresh = profile.max() * 0.35 if profile.max() else 0
    idx = np.where(profile > thresh)[0]
    # collapse runs of adjacent rows/cols into one position each
    groups, run = [], [idx[0]] if len(idx) else []
    for p in idx[1:]:
        if p - run[-1] <= 3:
            run.append(p)
        else:
            groups.append(int(np.mean(run)))
            run = [p]
    if run:
        groups.append(int(np.mean(run)))
    return groups


def calibrate(positions: list[int], nominal_spacing_ft: float) -> dict:
    """Pixels-per-foot from the modal gap between evenly spaced rules."""
    if len(positions) < 3:
        return {"ok": False, "reason": "too few rules found"}
    gaps = np.diff(positions)
    med = float(np.median(gaps))
    # keep gaps within 25% of median (drops doubled/missed rules)
    good = gaps[(gaps > med * 0.75) & (gaps < med * 1.25)]
    if len(good) < 2:
        return {"ok": False, "reason": "gaps not regular"}
    px_per_unit = float(np.mean(good))
    return {
        "ok": True,
        "n_rules": len(positions),
        "n_regular_gaps": int(len(good)),
        "px_per_spacing": round(px_per_unit, 2),
        "spacing_cv_pct": round(100 * float(np.std(good)) / px_per_unit, 2),
        "px_per_ft": round(px_per_unit / nominal_spacing_ft, 3),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tif", required=True)
    ap.add_argument("--waterline-spacing-ft", type=float, default=1.0,
                    help="drawn spacing between waterlines; VERIFY against "
                         "the drawing's own labels before trusting output")
    ap.add_argument("--out", default="grid_calibration.json")
    a = ap.parse_args()

    gray = load_region(a.tif)
    bw = binarize(gray)
    print(f"body-plan region: {gray.shape[1]}x{gray.shape[0]} px")

    wl = find_rules(bw, "h")
    bt = find_rules(bw, "v")
    print(f"  horizontal rules (waterlines): {len(wl)}")
    print(f"  vertical rules (buttocks/sta): {len(bt)}")

    cal_h = calibrate(wl, a.waterline_spacing_ft)
    print("\nvertical scale from waterline spacing:")
    for k, v in cal_h.items():
        print(f"  {k:20s} {v}")

    result = {
        "region_px": [int(gray.shape[1]), int(gray.shape[0])],
        "waterline_rows_px": wl,
        "buttock_cols_px": bt,
        "vertical_calibration": cal_h,
        "assumed_waterline_spacing_ft": a.waterline_spacing_ft,
        "WARNING": "spacing assumption is an INPUT, not a measurement. "
                   "Confirm against the drawing's labelled waterlines before "
                   "any offset is derived from this calibration.",
    }
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=1)
    print(f"\nwrote {a.out}")

    # visual proof: overlay detected rules
    vis = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    for y in wl:
        cv2.line(vis, (0, y), (vis.shape[1], y), (0, 0, 255), 2)
    for x in bt:
        cv2.line(vis, (x, 0), (x, vis.shape[0]), (255, 0, 0), 2)
    small = cv2.resize(vis, (vis.shape[1] // 2, vis.shape[0] // 2))
    cv2.imwrite("grid_overlay.png", small)
    print("wrote grid_overlay.png (red=waterlines, blue=buttocks/stations)")


if __name__ == "__main__":
    main()
