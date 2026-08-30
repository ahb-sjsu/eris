# Trim tabs, interceptors, and what the lines plan shows

2026-08-30. Computed by `software/analysis/trim_regime.py`; hull observations
read from `drawings/` at full scan resolution (8382×4047 lines plan).

## Short answer

**At your cruise speed, trim tabs and interceptors will not help — they will
cost you.** At full speed they begin to make sense. The dividing line is
about 12 knots on this hull, and you cruise at 9.6.

## Why: the regime decides, not opinion

Stern lift devices work by generating downforce on the water aft, which
pitches the bow down and alters running trim. That only matters once the
hull is developing enough dynamic lift to change its own trim with speed.
The governing parameter is Froude number:

| Condition | Speed | Fn | S/L | Regime |
|---|---|---|---|---|
| **Cruise** | 9.6 kt | **0.323** | 1.09 | **upper displacement** |
| Max (approx, verify) | 14 kt | 0.472 | 1.59 | semi-displacement |

Stern lift devices begin to earn their drag around **Fn 0.40**, which on a
78-ft waterline is **11.9 kt**. You cruise at 81 % of that threshold.

At Fn 0.32 the boat is supported by buoyancy, running at essentially its
static trim. There is no dynamic bow-rise for a tab to correct. What a tab
would add is wetted surface, appendage drag, and two more things to
maintain, service, and fair — against no measurable fuel benefit. On a
vessel whose defining virtue is 47 ton-miles per gallon, that is a bad
trade.

**Where they would genuinely pay:** if you run the boat hard. At 14 kt
(Fn 0.47) the hull is into semi-displacement, squatting and dragging its
transom, and stern lift starts to reduce resistance. If sustained
high-speed running is part of the mission, revisit this — but note that
running at Fn 0.47 costs far more fuel than tabs could ever recover, so the
decision is about speed, not about tabs.

## The three things that *do* pay at Fn 0.32

Since you asked the efficiency question, these are the levers that actually
move the number at your operating point:

1. **Static trim and weight distribution.** At displacement speeds the boat
   runs at the trim you load it to. With 2,026 gal of fuel in wing tanks
   plus 1,500 gal of water, the loaded-versus-empty trim difference is
   substantial, and optimum trim is usually slightly down by the stern but
   not much. This is free to test: run a measured mile at fixed rpm at
   several trim states and read fuel flow. **The twin is exactly the
   instrument for this.**
2. **Transom immersion.** A transom that drags submerged at low speed
   separates the flow and makes drag. The lines plan shows the buttocks
   running out flat and exiting at the transom (see below), so the
   at-rest transom immersion is worth measuring alongside the boot top.
   Correcting it is a weight-distribution question, not a tab question.
3. **Appendage and hull fouling.** At this Fn, frictional resistance is the
   dominant term, not wavemaking. A foul bottom, rough plating, and
   oversized or misaligned appendages cost more than any trim device could
   return. Antifouling discipline (there is an Interspeed data sheet in
   `Documents/personal/yacht/`) beats hydrodynamic gadgets here.

## On "built-in tabs" — what the drawings actually show

Read at full resolution, the body plan's after body shows a **markedly flat
run aft with a hard turn of bilge**, the sections flattening progressively
toward the transom. That flat run is what gives this hull its ability to
carry speed into the semi-displacement range without squatting badly, and
it is very likely what has been described to you as built-in trim
assistance. **Functionally that is fair: a flat run aft does the job a
wedge does, by shaping the hull rather than bolting something on.**

What I could **not** confirm from these scans:

- A discrete **stern wedge** (a fixed triangular section welded to the
  bottom just forward of the transom). This is the classic "permanent trim
  tab" and it would be a small feature — a few inches deep — at the very
  edge of what a 1960s blueprint scan resolves. It is neither visible nor
  ruled out at this resolution.
- Whether Eris matches the Point Barnes drawings here at all. Barnes is a
  **sister ship, not this ship**; hull details varied across the class's
  long production, and Eris has been modified since.

**How to settle it in ten minutes at the next haul-out:** sight along the
bottom aft, just forward of the transom, and look for a step or wedge in
the plating. Photograph the transom bottom edge and the run for the last
6–8 feet. That one photo answers the question permanently and belongs in
`drawings/`.

## Hull digitization: status

Started, not finished, and the honest reason matters.

**Done:** the drawing set is inventoried and readable at full resolution.
The body plan is legible enough for offsets — stations, waterlines, and
buttocks are all resolvable, with the after body left of centerline and the
forward body right.

**Not done:** a verified table of offsets. Extracting one from a 1960s
blueprint scan is not a single automated pass. The grid must be calibrated
against the drawn scale, every station curve traced, each waterline
intersection read, and the result faired and cross-checked against the
profile and half-breadth views — with manual verification at every step,
because a mis-read intersection propagates silently into displacement and
stability numbers that look plausible and are wrong.

**Why that matters here:** the digitized hull's purpose is to produce a
*trustworthy* displacement and stability picture before serious offshore
work. A fast, unverified trace would produce numbers with all the authority
of real ones and none of the reliability. That is the wrong failure mode for
this particular artifact.

**Recommended path, cheapest first:**

1. **Ask the Coast Guard Historian's Office / NARA for the original offset
   table.** Point-class design records may survive, and a published offset
   table beats any trace of a scan. One email, potentially the whole job.
2. If not: trace the body plan station-by-station with manual verification,
   loft in FreeCAD or DELFTship, and validate against the class's published
   displacement at design draft. That validation step is non-negotiable.
3. Either way, an inclining experiment on the actual boat is what makes the
   stability numbers real, given the conversion changes (masts, boom,
   leeboards, any crane).
