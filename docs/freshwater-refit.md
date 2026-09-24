# Fresh water refit: PVC to PEX

Scope: the potable system only — 1,500 gal tank, pump, accumulator, water
heater, hot and cold runs to sinks and showers. Raw water, sanitation, and
the fire main are out of scope and stay on their own materials.

## What is known (owner-confirmed 2026-09-24)

- The ship's original hot/cold fresh water piping, the hydronic HVAC
  (heating/chilling) piping, and the CO2 fire-suppression piping were all
  **removed, reason unknown**. What is aboard now is a PVC system the
  previous owner installed — so the refit is a **new design**, not a
  restoration; there is no original layout to follow.
- The only original metal piping left is the **fire main: 2 in heavy-wall
  copper, seawater**, fed from the auxiliary sea chest it shares with both
  generators. Each main engine has its own sea chest. The fire main is
  completely separate from fresh water, and must stay that way.
- AC is 120/240 V split-phase (`docs/phase1-lld.md`), so AC pump and heater
  are options; what is actually fitted is not recorded.

## Proposed design (pending the survey below)

- **PEX-A**, red/blue color-coded.
- **3/4" trunk** tank → strainer → pump → accumulator → heater and cold
  distribution. On a vessel this length, 1/2" trunk plus insert-fitting
  restrictions gives weak showers.
- **Zone manifolds** (e.g. forward accommodation, galley, aft heads), hot
  and cold, one valve per fixture, 1/2" home runs from each. Per-fixture
  isolation without 80 ft home runs.
- **Stainless cinch clamps + PPSU fittings** for most joints (small tool,
  no copper rings in salt air). Push-fit or unions only at serviceable
  equipment: pump, accumulator, heater, filters.
- **Thermostatic mixing valve** at the heater outlet (PEX is rated 180 °F at
  100 psi; engine-coolant heating can exceed that), heater relief valve
  kept and led somewhere sensible, **heater bypass** for winterizing.
- **Flexible reinforced hose** each side of the pump for vibration.
- Supports every 2–3 ft, chafe protection at every bulkhead, clear of
  exhaust and engine surfaces, no UV exposure.
- **Hot-water recirculation loop**: decide once fixture locations are known.
- Leave routing space for a future HVAC replacement.

### Open questions this design depends on

- **Regulatory:** if Eris ever carries passengers for hire (Subchapter T,
  flagged in `docs/research-expedition-assessment.md`), USCG rules on
  nonmetallic piping and bulkhead penetrations apply. Not researched yet;
  settle before buying pipe if that path is live.
- **Why the systems were removed.** One possibility for 1960s piping is
  asbestos lagging — a guess, not a finding. Any leftover lagging or
  hangers get tested before cutting or drilling near them.

## Survey list for Jim

Record what is there; "unknown" is a fine answer. Photos of every label.

**1. Water tank (1,500 gal)**
- Location, and outlet height relative to the pump inlet
- Outlet fitting size and thread
- Fill, vent, and level sender — what exists, condition
- Shutoff valve at the tank outlet?

**2. Pump**
- Make, model, voltage (AC/DC), rated flow and pressure
- Inlet/outlet port size and connection type (thread, barb, push-fit)
- Strainer before it? Size and condition
- Pressure switch cut-in/cut-out, if marked
- Mounting — on vibration isolators?

**3. Accumulator**
- Make, model, capacity, pre-charge pressure (if a gauge can be put on it)
- Connection size and type

**4. Water heater**
- Make, model, capacity (gal)
- Electric element voltage and wattage
- Also heated by engine coolant? From which engine?
- Inlet/outlet sizes; relief valve and where it drains
- Any mixing valve or winterizing bypass now?

**5. Fixtures**
- Every sink, shower, freshwater-flush head, deck wash, ice maker — with
  location (deck and compartment)
- Hot/cold or cold only, and connection size at each faucet

**6. Existing PVC**
- PVC or CPVC? (printed on the pipe) — **especially the hot lines**
- Trunk and branch sizes
- Rough routing sketch: main runs, bulkhead penetrations, anything
  through the engine room
- Known leaks, repairs, or re-glued joints

**7. Other**
- Filters or treatment (UV, carbon): model and connections
- Any watermaker, or space/power reserved for one
- Accessible spaces for zone manifolds (forward, midships, aft)

**8. Removed systems and bulkhead penetrations**
- Every hole left by removed piping (fresh water, HVAC, CO2): location,
  size, and **open / plugged / properly sealed**
- Which bulkheads are watertight or fire-rated, and whether any of these
  holes are in them
- Leftover pipe stubs, hangers, brackets, insulation — photos
- Any paperwork on when and why the systems were removed (surveys, yard
  invoices, previous owner)

**9. Fire protection now**
- Current engine-room fire protection: fixed system, extinguishers,
  detection
- Fire pump make, model, motor rating
- Condition of the 2" copper fire main: weeping joints, green/white
  deposits, especially where it is mounted against the steel hull
- Can the fire pump and both generators draw from the shared auxiliary
  sea chest at full demand at the same time? Is there a blow-out
  connection, or a crossover from a main's chest?

**Photos:** pump, accumulator, heater (labels and plumbing), tank outlet, a
typical bulkhead penetration, engine-room runs.

---

*Answers go into `schema/points.yaml` (`freshWater`, `removedSystems`,
`firePump`, `topology.rawWater`) with the date, replacing the TBDs.*
