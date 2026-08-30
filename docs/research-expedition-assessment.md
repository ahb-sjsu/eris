# Eris as a research / expedition yacht — an assessment

Written 2026-08-30 from the drawing set, the recorded plant facts in
`schema/points.yaml`, the profile photo, and published Point-class history.
Numbers derived from this repo's data are marked; class figures are marked;
nothing else is asserted. Where the honest answer is "measure it," the
roadmap item that measures it is named.

## The short version

The bones are unusually good. This hull was designed for exactly the duty
cycle an expedition vessel lives: multi-day offshore patrol in weather, with
machinery redundancy a yacht of this size never gets. The conversion's
existing features — crane-rated hydraulics, 440 V three-phase generation,
fuel polishing, shallow draft — read like a small research vessel's spec
sheet already. The limiting factors are range (coastal-expedition yes,
ocean-crossing marginal until measured), accommodations (a layout question
the decks drawing can answer), and the age of a 1960s steel hull (a survey
question, not a paperwork one).

## What the platform brings, from the record

**Purpose-built seakeeping.** The Point class was designed for search and
rescue and offshore patrol — station-keeping, towing, bad-weather work with
a small crew. The lines plan in `drawings/` shows the soft-chine
displacement hull that made the class famously seakindly for 82 feet. This
is the opposite inheritance from a converted motoryacht: the hull was never
asked to be pretty at anchor.

**Machinery redundancy, already documented in the schema:**
- Twin mains (VT900M/VT1710), each with its own sea chest and duplex strainer
- Twin 20 kW gensets on a separate shared chest, duplex strainers each
- Electric fire pump with port/starboard stations
- Three independent 24 V start banks
- A fuel-polishing system (100→30→10 µm) — *the* defense against the
  classic expedition-killer, bad fuel from a remote dock

That inventory is a redundancy posture most sub-100-ft yachts simply do not
have, and it is the difference between an inconvenience and a mayday when
something fails 400 nm from a mechanic.

**Science-handling potential in the hydraulics.** The lazarette power unit
was sized for a transom crane the Navy removed. That standing headroom is
precisely what over-the-side science asks for: an A-frame or davit for
instrument packages, a winch for CTD/sampling casts, recovery of a small
ROV or workboat. The circuit may still be plumbed (open gap in the schema);
if it is, the single most research-enabling upgrade on this boat is a
reinstalled stern crane on Navy-spec plumbing. The yellow boom already
rigged (profile photo) covers lighter lifts today.

**Lab-grade electrical power.** 2×20 kW of 440 V three-phase is generous
for this size. The delta/floating-neutral arrangement is the classic marine
IT system: the first ground fault degrades nothing and trips nothing —
continuity of service, which is why ships use it. Two consequences worth
stating: it will run real equipment (compressors, winches, machine tools,
a serious inverter front-end), and it *requires* ground-fault monitoring to
keep its fault tolerance honest (candidate schema point).

**Shallow draft.** Class draft is under six feet (verify against the lines
plan at digitization). For expedition use this is a genuine feature:
gunkholing, river mouths, atoll lagoons, and haul-outs at yards a deeper
vessel cannot reach.

**Water.** 1,500 gal (recorded) is roughly two weeks for six people at
liberal use without a watermaker — comfortable, and a watermaker makes it
moot.

**The twin itself.** A vessel whose plant is instrumented to
`schema/points.yaml`, logging to VictoriaMetrics, with process models and a
BMS, is *already* a research platform in the instrumentation sense — and a
floating lab for the owner's own teaching (IoT, data mining on live vessel
telemetry, digital-twin coursework).

## Range: the honest number is parametric until measured

Recorded fuel: 2,026 gal total (2×920 wing + 186 day). Range depends on
combined burn at cruise, which this repo does not yet know. Parametrically,
at displacement cruise (call it 9 kt) with a 10 % reserve:

| Combined burn (gph) | Endurance (h) | Range (nm @ 9 kt) |
|---|---|---|
| 8  | 228 | ~2,050 |
| 12 | 152 | ~1,370 |
| 16 | 114 | ~1,025 |
| 20 | 91  | ~820   |

Reading: **coastal expedition (Inside Passage, Baja, Caribbean chains,
Great Loop) is comfortably in reach on any plausible burn; transoceanic legs
are not, without either a measured low burn at slow cruise or auxiliary
propulsion.** Two notes from the record: the engine-room notes already
link a fuel-flow sensor — the twin's fuel-flow channels turn this table
into one measured number. And the active-leeboard project plus the stepped
masts suggest sail-assist is already contemplated; measured motorsailing
burn reduction would extend range materially *and* is a publishable
experiment in its own right on a hull like this.

## What the record does not yet support

- **Accommodations.** Cutter berthing was ~8–10 crew in patrol austerity.
  How that converts to owner + guests + a science party is a layout
  question; the decks drawing supports the analysis but it has not been done.
- **Stability with conversion changes.** Masts, boom, leeboards, and any
  crane change the weight and windage picture. The hull digitization
  (roadmap) plus a modern inclining test is the responsible path before
  serious offshore work.
- **Hull condition.** A 1960s mild-steel hull is a plating-survey question.
  Nothing in this repo speaks to it either way; an ultrasonic survey is the
  input the assessment lacks most.
- **Black/gray capacity, watermaker, HVAC** — recorded gaps; all three are
  endurance factors for a live-aboard science party.
- **Regulatory scope.** As a private yacht doing the owner's research with
  guests, minimal friction. Carrying paying scientists or students for hire
  moves the vessel toward inspected-vessel territory (US Subchapter T/R
  analysis needed before any such plan).

## Verdict

As a **coastal research/expedition yacht** — instrument casts over the
stern, student cruises, long seasons in Alaska or Baja, a floating
data-systems lab — Eris is not merely viable; the platform is close to
purpose-shaped, and the missing pieces (crane reinstatement, ground-fault
monitor, watermaker, accommodations layout) are ordinary refit items, not
structural surgery. As an **ocean-crossing expedition vessel**, the honest
answer is: measure the burn, digitize the hull, survey the plating, and
revisit — the range table above says the door is open at the low-burn end,
and sail-assist could hold it open.

The next three roadmap items are exactly the three measurements this
assessment is waiting on: fuel flow (range), hull digitization
(displacement/stability), and the plumbing check in the lazarette (crane).
