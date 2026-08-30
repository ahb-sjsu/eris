# Measurements wanted aboard

Prioritized. Every item says *why*, so you can skip anything that costs more
than it's worth on the day.

## If you only do three things

1. **Photograph the bottom aft, just forward of the transom.** Sight along
   the hull bottom for the last 6–8 ft and shoot the transom bottom edge.
   → Settles the "built-in tabs" question permanently: is there a discrete
   **stern wedge** (a welded step/wedge), or is the trim assistance purely
   the flat run aft that the body plan shows? Currently neither confirmed
   nor ruled out at scan resolution.

2. **Length on the waterline (LWL).** Bow-to-stern along the actual
   waterline (boot top is fine, note which you used).
   → Every efficiency number in `docs/` currently rests on an **assumed
   78 ft**. LWL sets Froude number, hull speed, the trim-tab threshold, and
   the ton-mile figures. This is the single largest source of error in the
   analysis right now.

3. **Maximum beam**, and where along the length it occurs.
   → The validation that matters most: if beam matches the class figure,
   the Point Barnes drawings can be trusted for Eris. If it does not, the
   drawing set is a reference rather than a model, and the digitization
   plan changes.

## Hull, for digitization ground truth

Record the **load state** with these (fuel and water tank levels), since
draft and trim depend on it.

4. **Draft** forward and aft — from draft marks if legible, else waterline
   to bottom of keel.
5. **Freeboard** at bow, midships, and stern (deck edge to water).
   → 4 + 5 together give current trim, which is the baseline for the
   trim-optimization experiment.
6. **Transom immersion at rest**: how far below the waterline does the
   transom bottom edge sit? Even "about 8 inches" is useful.
   → A dragging immersed transom is a real drag source at Fn 0.32, and it
   is correctable by weight distribution rather than by hardware.
7. **LOA on deck**, stem to transom.
   → Cross-check against the drawing scale.

## Nameplates — photos are enough, no transcription needed

8. **Main engine data plates** (both) → confirms the VT900M rating; the
   low-load percentage in the efficiency analysis is estimated against an
   assumed rating.
9. **Hydraulic power unit** → driver (electric vs PTO) and rating; open
   schema gap.
10. **Fire pump motor** → rating; open schema gap.
11. **Genset data plates** → confirms the 20 kW and 440 V figures.
12. **Battery labels** → group size / CCA / Ah, and chemistry (the BMS SoC
    table assumes flooded lead-acid; if they are AGM the voltage thresholds
    shift).

## Quick observations worth noting if convenient

13. Is there a **house/domestic battery bank** separate from the three
    starting banks, or does everything run off those? (Largest open
    electrical gap.)
14. **Black/gray tank capacities** if labelled.
15. Does the **transom crane circuit** still have plumbing in the
    lazarette — capped hydraulic runs going aft? → decides whether crane
    reinstatement is a bolt-on or a re-plumb, which is the single most
    research-enabling upgrade identified in the assessment.
16. Any **stern wedge, bilge keels, or trim devices** already fitted.

---

*Anything measured here should be added to `schema/points.yaml` (plant
facts) or `docs/` (hull facts) with the date, and it supersedes any
estimate in the analysis scripts — `software/analysis/*.py` all read their
inputs from constants at the top of the file for exactly this reason.*
