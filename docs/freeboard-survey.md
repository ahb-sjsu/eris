# Freeboard survey — protocol

The measurement that yields displacement. Drawings give hull sections above a
baseline; freeboard locates the real waterline against them. Subtract, and
every section's immersed area is known; integrate, and that is displacement
and LCB. This is the input that turns the validated Barnes geometry into
numbers about *Eris in her present condition*.

## What to measure

**Freeboard = vertical distance from the waterline up to the DECK EDGE** —
the sheer, where the hull plating meets the deck. Not the top of the
bulwark or rail.

If reaching the deck edge is awkward, measure to the **top of the bulwark**
instead — that is fine, **as long as you say so and measure bulwark height
once**, so the two are reconcilable.

## Where

**Six to eight stations**, spread bow to stern, each recorded as *distance
from the transom* (measure along the deck; exact is better than round).

Suggested spacing on a ~82 ft hull — adjust to whatever is reachable:

| # | ~ft from transom | why this one |
|---|---|---|
| 1 | 5 | captures stern trim; near the transom |
| 2 | 15 | |
| 3 | 25 | |
| 4 | 32 | near max beam (0.39 of length) |
| 5 | 45 | |
| 6 | 58 | |
| 7 | 70 | forward sections, where flare matters most |
| 8 | 78 | near the stem |

Port or starboard is fine. **Both sides at one or two stations** is a useful
check on list — if they differ, note it, because a permanent list changes
the displacement calculation.

## Record alongside the numbers

These decide what load condition the answer describes:

- **Fuel**: level in each wing tank and the day tank
- **Water**: level in the 1,500 gal tank
- Anything unusual aboard (tender, gear, ground tackle deployed)
- Date and rough sea state — measure in flat water, at the dock, not in chop

## Also useful, same trip

- **Draft at the transom** and **at the stem**, if there are marks or you can
  sound it. Recorded so far: **about 6 ft** (owner, 2026-08-30). Two draft
  readings plus the freeboards over-determine the problem, which is good —
  the redundancy is what catches a bad measurement.
- **Transom immersion**: how far below the waterline the transom bottom edge
  sits. Feeds the drag question in `trim-devices-and-hull-digitization.md`.

## What comes out of it

1. **Trim** — from the freeboard slope, directly.
2. **Draft at every station**, not just fore and aft.
3. **Displacement** — integrate immersed section areas along the length. The
   current 69 LT figure is a class estimate; this replaces it with a measured
   one for a known load state.
4. **LCB** (longitudinal centre of buoyancy) — falls out of the same
   integration, and it is what the trim-optimization experiment needs.
5. A **validation loop**: displacement computed this way, compared against
   the class figure, is the check on the whole digitization chain. If they
   agree, the traced sections are trustworthy. If they do not, one of the two
   is wrong and we find out which before anyone relies on a stability number.

## Precision worth caring about

Nearest **inch** is plenty. The waterline moves more than that with wake and
fuel burn. Do not chase fractions; do get the station distances right, since
an error there mislocates the section and matters more than an inch of
freeboard.
