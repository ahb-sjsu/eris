# Phase 1: low-level design

Companion to `solar-rail-module-spec.md` (the "spec"). The parts list is in
`phase1-bom.csv`. The same source tags apply: **[LISTING] [ASSUMED]
[DERIVED] [DECISION]**. Every [DECISION] is the owner's to revise.

## 0. Scope

Phase 1 builds one of everything, the smallest system that proves the full
chain end to end:

| Unit | Qty | What it is |
|---|---|---|
| Rail assembly, port | 1 | 2 panels + 1 rail module (RM) + mount + wiring |
| Rail assembly, starboard | 1 | same |
| Leaf 62 kWh pack | 1 | used pack, its own battery controller (LBC) and internal contactors |
| Hold cabinet | 1 | DC bus, fuses and disconnects, supervisor, network |
| Battery interface module (BIM) | 1 | the one pack interface; the cabinet has room for more |
| Inverter module (IM-3500) | 1 installed + 1 spare | **3.5 kVA per module**, paralleled to scale |

How this differs from the spec:

- **2 panels per RM (2S), not 4.** Same RM hardware; the input simply sits
  low in the MPPT window (spec section 2). Phase 1 solar is ~0.8 kW
  realistic, ~1 kW nameplate.
- The spec left the load side out of scope. This document designs it: a
  modular inverter in 3.5 kVA steps.
- **Fold-out panels: reserved, not built** (§6.1). Each rail panel will later
  carry a second panel on a top-edge piano hinge. Phase 1 builds the
  structure, cable and cabinet space for them and buys nothing else.
- **Trackers are deferred.** Phase 1 mounts are fixed tilt with manual pin
  positions. The tracker spec is still an open item.

## 1. Phase 1 block diagram

```
PORT RAIL                          HOLD CABINET (IP66 steel, DIN + busbars)
[P][P]--MC4-->[RM-P]==6mm² pair==>[F 10A]-[ISO]-+
                  |                             |      +BUS/-BUS (100 A Cu busbar)
STBD RAIL         |                             |  +------+-----------+----------+
[P][P]--MC4-->[RM-S]==6mm² pair==>[F 10A]-[ISO]-+  |      |           |          |
                  |                                [SPD]  [IMD]   [F 20A]    [F 20A]
                  |                                                 |          |
                  |                                             [IM-3500 #1] [slot #2]
                  |                                                 |  AC out 120/240 V
                  |                                                 v  split-phase 60 Hz
                  |                                              [AC test panel]
                  |          BIM:  +BUS--[NH F 40A]--[ISO 63A]--(pack HV+)
                  |                -BUS-------------[ISO]-------(pack HV-)
                  |                LEAF PACK (internal SMR+, SMR-, PRE)
                  |                   ^ 12 V coils, 12 V wake   ^ CAN (LBC)
                  |                [contactor drivers]<--[Battery-Emulator board]
                  |                                             ^ CAN0 (battery protocol)
   Cat6 PoE ------+------------>[PoE switch]--Eth--[SUPERVISOR (Pi 5 + 2-CH CAN)]
                                                    CAN1 + sync pair --> IMs
   E-STOP loop (hardwired): opens pack contactors, drops IM enables, cuts PoE
   24 V house battery --> 24->12 V (LBC, contactors), 24->48 V (PoE), 24 V (IM aux)
```

## 2. Hold cabinet: the modular DC bus

The cabinet is a backplane. Every power unit hangs off the common +BUS/−BUS
through its **own fuse and its own disconnect**, so each one can be taken out
while the others run.

| Feeder | Phase 1 fuse | Disconnect | Cable | Scales to |
|---|---|---|---|---|
| Pack (via BIM) | NH1 gPV **40 A** in a 160 A holder | DC load-break isolator ≥ 600 V, ≥ 63 A | 25 mm² H1Z2Z2-K | swap to 100 A fuse and isolator as IMs are added (§2.1) |
| Rail side, per side | 10×38 gPV **10 A** | 2-pole DC isolator 1000 V, 32 A | 6 mm² H1Z2Z2-K | 20 A fuse at 3 RMs/side (spec §8.2) |
| Each IM | 10×38 gPV **20 A** | 2-pole DC isolator 1000 V, 32 A | 4 mm² H1Z2Z2-K | one feeder per IM |
| Bus SPD | per SPD maker | — | short | — |
| Bus insulation monitor | internal | — | — | — |

- **Busbars:** copper, ≥ 100 A, on DIN busbar insulators, with a finger-safe
  cover. [DECISION] 100 A is enough for the full 24-panel array, the 24
  reserved fold-outs (~35 A total solar at 350 V) and 6 IMs
  (§2.1).
- **Bus SPD:** a solar-industry Type 2 PV SPD (1000 V DC). The rail runs are
  long exposed conductors on a steel ship with a radar mast.
- **Insulation monitor (IMD):** an EV-type IMD, e.g. Bender IR155-series,
  between the bus and hull ground. Its fault output goes to the supervisor and
  into the E-stop logic (warn, then trip).
- Label every door and cover "350 V DC".

### 2.1 Scaling arithmetic [DERIVED]

- Each IM draws at most 3.5 kVA / 0.95 / 300 V ≈ **12.3 A** at the pack's
  low-voltage cutoff.
- The pack main fuse must carry n × 12.3 A plus the solar input (~22 A at the
  full 24 panels). 40 A covers 2 IMs; 100 A covers ~6 IMs, ~21 kVA.
- Past ~6 IMs, add a **second pack and a second BIM**, not a bigger fuse. The
  Leaf pack could deliver far more, but at 0.3C (~20 kW) a 62 kWh pack runs
  for three hours. Capacity, not current, sets when the next pack comes.

## 3. Battery interface module (BIM)

One BIM per pack. Its job: wake the pack, read it, close its contactors safely,
tell the supervisor the limits, and open everything on any fault.

### 3.1 Parts and roles

| Function | Implementation | Why |
|---|---|---|
| Leaf battery controller comms + contactor sequencing | **Battery-Emulator** firmware (github.com/dalathegreat/Battery-Emulator) on a LilyGO T-CAN485 or T-2CAN board | proven Leaf 62 kWh support; handles the Leaf quirks (below) |
| What the supervisor sees | the Battery-Emulator board's **inverter-side CAN output** (a standard home-battery protocol: charge voltage limit, charge/discharge current limits, SOC, alarms) | the supervisor reads a *generic* battery. A different pack chemistry later is a config change, not a rewrite |
| Contactor coils | Leaf internal SMR+, SMR−, precharge relay; **12 V coils**, flyback diode per coil, PWM hold at ~6 V after pull-in (Leaf practice) | the pack's own switchgear, rated for it |
| Coil drivers | 3 channels: automotive relays or SSRs driven from the Battery-Emulator board's contactor outputs | Battery-Emulator supports SSR PWM mode |
| 12 V for LBC and coils | 24→12 V DC-DC from the house battery, ≥ 10 A | house battery already aboard |
| Main fuse | NH1 gPV, in the BIM, **at the pack end** of the pack cable | the source-end fuse protects the cable |
| Maintenance disconnect | DC isolator; **off-load only**: open the contactors first | contactors break current, the isolator provides visible isolation |
| E-stop | series loop of NC mushroom buttons (hold, wheelhouse); breaking the loop drops coil power directly, in hardware | works even if every computer is hung |

### 3.2 Contactor sequence [DECISION]

```
OFF -> WAKE (12 V to LBC, wait for CAN) -> CHECK
CHECK: LBC no faults, IMD OK, E-stop loop closed, supervisor "inverter OK"
       (Battery-Emulator closes only when BOTH battery and inverter say OK)
-> PRECHARGE: close SMR- and PRE; bus rises through the pack precharge resistor
   wait until V_bus >= 0.95 x V_pack (bus voltage sensed by the BIM), timeout 3 s -> FAULT
-> CLOSE SMR+, then open PRE  -> ON
ON -> any fault / E-stop / supervisor off -> ramp IM and RM current to 0 (≤ 200 ms) -> open SMR+ then SMR-
```

- **Bus capacitance limits precharge.** The Leaf's internal precharge resistor
  was sized for the car's inverter. Total bus capacitance (all IM inputs + RM
  outputs + cabling) must be checked against it. If it is too large, IMs
  precharge their own input (§4.5) *after* the pack closes. **Open item:
  measure the Leaf precharge resistor.**
- **Periodic LBC reset.** Battery-Emulator's Leaf page notes that 40/62 kWh
  packs drift out of balance long-term if the battery controller is never
  restarted, so a periodic reset is mandatory. The supervisor schedules it at
  night, with IMs on reserve (or loads briefly off) since the contactors open.
  [DECISION: weekly, 03:00]
- **Pack low-voltage cutoff: 300 V** (3.125 V/cell average) [DECISION]. It
  gives up a few percent of capacity to keep the IM's link voltage high enough
  for 240 V (§4.2). Cell-level limits from the LBC come first; 300 V is the
  pack-average floor.

### 3.3 Pack mounting (hold)

- Steel cradle bolted to structure; the pack strapped down, on rubber
  isolators; **~400+ kg [ASSUMED], weigh it**.
- A 62 kWh pack is ~40 mm taller than earlier Leaf packs (Battery-Emulator
  wiki). Measure the pack in hand before building the cradle.
- Ventilation: forced air through the battery space, exhausting outside the
  hull. Heat and smoke detection wired to the supervisor **and** to the
  wheelhouse alarm independently. The fire plan (ABYC E-13) is still an
  open item.

### 3.4 Licence note

Battery-Emulator is GPL-3.0. Running it unmodified on its own board creates
no obligation. If we fork it, our changes to *that firmware* are GPL-3.0.
Talking to it over CAN from the supervisor does not bring the supervisor
under GPL.

## 4. Inverter module IM-3500

### 4.1 Ratings

| Parameter | Value | Source |
|---|---|---|
| Output | **120/240 V split-phase, 60 Hz** (L1, L2, N) | [DECISION] North American boat standard |
| Alternate output (config) | 230 V 50 Hz L1–L2 (115 V per leg) for international gear | [DECISION] same hardware, firmware setting |
| Continuous | **3.5 kVA** total; per leg ≤ 2.5 kVA (21 A) for unbalanced loads | [DECISION] |
| Surge | 1.5× for 5 s (motor starts) | [DECISION] sets device and inductor sizing |
| DC input | pack bus 300–403 V (runs 250–420 V; derated below 300 V) | [DERIVED] spec §3, §3.2 |
| Isolation | **galvanic**, pack to AC | [DECISION] keeps the DC bus floating; AC neutral can be bonded per ABYC |
| Parallel | up to 7 on one bus (fuse and busbar limit, §2.1) | [DERIVED] |
| Direction | Phase 1: DC→AC. **Hardware bidirectional** (shore charging = firmware, Phase 2) | [DECISION] |
| Efficiency target | ≥ 93 % at 50–100 % load | [ASSUMED] 2 stages at ~96–97 % each |
| Aux power | 24 V house battery (NOT PoE; see §4.6) | [DECISION] |

### 4.2 Topology

```
BUS 300-403 V -> [precharge] -> [LLC-DCX, 1:1.25, at resonance] -> LINK 375-504 V -> [3-leg bridge: L1, L2, N] -> [LC per leg] -> [AC relay] -> L1/L2/N
```

- **Stage 1, LLC DC transformer, turns ratio 1:1.25.** Same idea as the rail
  module's second stage: runs unregulated at its resonant frequency for
  efficiency and isolation. Link voltage V_link = 1.25 × V_bus = **375–504 V**
  [DERIVED].
- **Why 1:1.25:** 120 V per leg means ±170 V peak about a neutral leg held at
  V_link / 2, so V_link must be ≥ 340 V plus ~10 % for modulation and filter
  drop, i.e. **≥ 375 V**. That is reached at a 300 V bus, which is exactly why
  the pack cutoff is 300 V (§3.2). [DERIVED]
- **Stage 2, a three-leg (four-wire) split-phase bridge.** Legs L1 and L2 at
  180°, and a third leg actively forming the neutral. The neutral leg carries
  imbalance current, so it is rated like a phase leg (21 A).
- **One MOSFET part number for all 14 switches**: 8 in the DCX (primary and
  secondary full bridges; secondary switches are synchronous rectifiers,
  which also makes the module bidirectional) and 6 in the bridge. **1200 V
  SiC, TO-247** [DECISION]. 1200 V at a 504 V link is generous margin (spikes,
  salt, a cold start), and a single part means a single spare type aboard.
- **Link capacitance:** a split-phase bridge draws 120 Hz ripple power. For
  ±20 V ripple at 3.5 kVA and 400 V: C ≈ P / (2π·120·V·ΔV) ≈ **580 µF**
  [DERIVED]. Use two 1200 µF / 450 V electrolytics in series with balancing
  resistors (600 µF, 900 V), plus film decoupling at each leg. This keeps the
  ripple off the pack.
- **Output filter:** LC per leg (≈ 0.5 mH powder-core inductor rated 25 A
  RMS/35 A peak, 10 µF X2 film capacitor) [ASSUMED starting values; set by
  switching frequency in design].
- **Output relay:** 3-pole AC contactor (L1, L2, N), 40 A, DIN mount.

### 4.3 Paralleling and scaling: three layers, each a fallback for the next

1. **Sync pair (primary).** A dedicated twisted pair carries a
   zero-crossing pulse from the elected master IM (RS-485 levels). All IMs
   lock phase to it. Tight phase sharing, no dependence on software latency.
2. **CAN (setpoints and sharing).** The IMs share load measurements and
   voltage and frequency setpoints on CAN1. The supervisor sits on the same
   bus for configuration and limits.
3. **Droop (fallback, always active underneath).** Frequency droops with
   real power, voltage droops with reactive power, plus virtual output
   impedance. If the sync pair and CAN both fail, the modules still share load
   with no communication at all, just less precisely.

- **Master election:** lowest ID that is healthy. If the master drops, the
  next one takes over and holds phase by measuring the live AC bus: **every IM
  senses L1–N voltage and can lock to the bus itself**.
- **Scaling = add an IM:** fuse and isolator on the DC side, connect AC
  L1/L2/N to the AC busbar, CAN and sync daisy-chained, assign an ID. It hot-joins:
  precharge, lock to the AC bus, close its relay at matched phase, ramp its share.
- **Degraded operation:** with 2+ IMs, losing one leaves the rest carrying
  load, while load-shedding (supervisor) keeps them under rating.

### 4.4 Control and protection

| Item | Value |
|---|---|
| MCU | TI C2000 (F28003x class; LaunchPad in Phase 1), same family as the RM |
| Loops | per-leg voltage loop + inner current loop; DCX runs open-loop at resonance with soft-start |
| Output OC | per-leg hardware trip < 10 µs; firmware limit at surge rating |
| Short circuit | current-limit then trip after 100 ms (lets a downstream breaker clear) |
| Link OV / UV | trip at 540 V / sag handling below 360 V (derate below 375 V) |
| Bus UV | stop at bus < 300 V unless a firmware override has been set (not the default) |
| Over-temperature | heatsink, magnetics; derate then trip |
| Neutral-ground bond | relay bonds N to ground **only while this system is the AC source**, driven by the transfer switch's aux contact (ABYC E-11 practice, verify clause) |
| Anti-backfeed | refuses to close its output relay onto an AC bus fed by shore or a generator unless in parallel-capable mode (not in Phase 1) |

### 4.5 Start-up

1. Aux 24 V present, enable loop closed, BIM reports ON.
2. Close the input precharge relay (resistor), then the main input contactor
   at ≥ 95 % of bus voltage.
3. DCX soft-start (frequency sweep down to resonance) charges the link.
4. If this module is master: ramp AC voltage from 0 (soft start). If joining:
   lock to the AC bus, match, close the relay, ramp its share.

Input switchgear: an EV-style HV DC contactor, 12 V coil, ≥ 450 V, plus a small
precharge relay and resistor. EV contactors are everywhere EVs are
scrapped, and the Leaf's own contactors are this type.

### 4.6 Why the IM is not PoE-enabled (unlike the RM)

A rail module that stops costs a little sun, so it fails *off* whenever the
link to the hold drops. An inverter that stops drops the boat's AC loads. So
the IM:

- runs from **24 V house aux** and keeps running if the supervisor, switch or
  CAN fails, using its **last-received limits** and its own bus floor
  (300 V);
- still stops on the **hardwired enable loop** (E-stop, BIM contactor state)
  and on any local protection;
- the pack stays protected regardless. If the pack goes out of limits, the
  battery controller, via Battery-Emulator, opens the contactors, the bus
  collapses, and the IM stops.

## 5. Rail module, Phase 1 build (2S)

The spec's design, built as specified, with the input at 2S:

| Quantity | 2S value | Source |
|---|---|---|
| Vmp STC / hot 70 °C | 37.4 V / ~32 V | [LISTING]/[DERIVED] |
| Voc cold (−10 °C) | ~49 V | [ASSUMED] Voc, spec §2 |
| Power | ~420 W realistic, 500 W nameplate | [DERIVED] spec §2 note |
| Boost gain | V_int (96–134 V) / 32–49 V = 2.0–4.2 | [DERIVED] |
| Output current | ≤ 1.5 A at 288 V | [DERIVED] |
| Output fuse (in hold) | 10 A gPV (cable protection, not module protection) | [DECISION] |

**Build the full 1.1 kW board.** The Phase 1 input is well inside its ratings.
The same boards go to 4S in Phase 2 with no hardware change, and the spare
module is identical.

Key parts (see BOM for the full list): synchronous boost with 200 V Si
MOSFETs (TO-220); LLC-DCX primary full bridge with 200 V Si MOSFETs, 1:3
ferrite transformer (ETD-class core, litz); **secondary with 650 V SiC
Schottky diodes** (bridge rectifier: no gate drive on the HV side, and it
blocks reverse current for free); isolated output sensing (AMC1311/AMC1301
class); PoE powered-device module (802.3af, 12 V out) feeding all gate drive;
output HV DC relay with its coil on PoE power; C2000 LaunchPad + W5500
Ethernet module.

**Reserved I/O for the tracker (§6.2).** The RM board is not yet laid out,
so reserve now: one H-bridge control output (PWM + direction) to an
external actuator driver, two limit-switch inputs, one analog position
input, one I²C port for a frame inclinometer/IMU, one input for the stow
reed switch (§6.1), and a spare cable gland. These cost nothing to reserve
now and a board respin to add later.

**Through-hole power parts, deliberately.** They can be replaced with a
soldering iron in a port, and TO-220/TO-247 parts have the widest
substitutes.

## 6. Rail assemblies (×2)

| Item | Detail |
|---|---|
| Panels | 2 × WERCHTAY 250 W model 2112 [LISTING], in series with their own MC4 leads |
| Mount | **Fixed tilt, manual pin positions** (−60/−30/0/+30/+60°, fore-aft axis) [DECISION; the frame pivots on tracker-grade bearings from day one, and the actuator comes later (§6.2)] on a frame of slotted strut channel (Unistrut-type, stainless or hot-dip galvanized) clamped to the rail stanchions with 316 SS U-bolts |
| Galvanic isolation | nylon/G10 isolating washers and sleeves wherever aluminium panel frames meet stainless or steel structure |
| Stow | 0° (flat) with the pin in, for weather |
| RM location | on the fixed rail structure (not the rotating frame) under a sun/spray shield |
| String wiring | panel leads → 4 mm² PV cable with MC4 → RM input gland, with drip loops |
| Array bonding | panel frames bonded to hull ground (safety earth). The *array conductors* stay floating (spec §7) |
| Down-run | **two** 6 mm² H1Z2Z2-K red/black pairs + **two** Cat6 outdoor per side (one pair and one Cat6 each for the rail panels and the reserved fold-outs; the unused set is also a **spare run**, spec §10), together, in UV-rated conduit or clipped every ~450 mm; glands at the deck penetration |
| Labels | "350 V DC" on the down-run at every access point; "PV, LIVE IN DAYLIGHT" on the string side |

### 6.1 Fold-out provision (top-edge hinge; build later)

Each rail panel will later carry a second, identical panel on a **316 SS
piano hinge along its top edge**. Deployed, it opens upward to double
the height; stowed, it folds down **back-to-back** onto the rail panel
(glass out on both sides, the fold-out facing inboard).

Built in Phase 1, so nothing has to be torn out later:

| Provision | Detail |
|---|---|
| Frame strength | rail frame, clamps and stanchion attachment designed for **2 panels per bay** (~2 × panel mass [ASSUMED ~9 kg each]) plus deployed wind load on the doubled height. Size the loads once the panel is chosen |
| Hinge line | top rail of the frame drilled/tapped for the hinge along its full length; isolating strip (G10/nylon) between the SS hinge and the Al panel frame |
| Deployed stay | two stay/gas-strut mount points per bay, set for the deployed angle; a positive latch for the stowed position (not gravity) |
| Stow sensor | a mount for one sealed reed switch per bay on the stow latch. Later the supervisor alarms if a fold-out is deployed while underway (speed over ground from Signal K) |
| Hinge cable | a clamped service loop of flexible 4 mm² PV cable, MC4s free of strain, clamped both sides of the loop |
| Down-run | second cable pair + second Cat6 per side pulled in Phase 1 (§8, W3F/W4F) |
| Cabinet | DIN space reserved for **two more rail feeders** (fuse holder + isolator) per side; the busbar rating already covers them (§2) |
| Rail modules | fold-outs get **their own string and their own RM**, never in series with the rail panels (a stowed fold-out would drag the rail string). Same RM board, no redesign |
| Network | the 8-port switch covers Phase 1 plus the first fold-outs. At full build (6 rail + 6 fold-out RMs = 12) add a second PoE switch or a larger one |

**Operating rule:** deploy only at anchor or alongside in settled weather;
latched stowed underway. Deployed height doubles windage and puts a lever
arm on the hinge.

### 6.2 Tracker provision (actuator + sun tracking; build later)

Phase 1 is manual pin positions. The tracker adds an actuator per side
(or per frame) and tracking software. Provisions built now:

| Provision | Detail |
|---|---|
| Pivot | fore-aft axis on **flanged bronze or UHMW bushings** sized for continuous tracking (not just a pin hole); the pin positions remain as the manual fallback |
| Balance | pivot placed near the frame's centre of mass **with the fold-out stowed**; deployed fold-outs shift it up. The tracker limits travel when the stow switch says deployed |
| Actuator mounts | welded/bolted clevis lugs on the frame and on fixed structure, geometry reserved for a **linear actuator** |
| Travel | a linear actuator practically gives about **±60°**. The spec's ±90° needs a slew drive (worm gear) instead. **Owner decision**; the lugs above suit a linear actuator |
| Power | a **24 V feed per side, pulled now** (W12, 6 mm² tinned duplex, fused in the hold). It is independent of the RM, so the tracker can still stow if an RM is dead |
| Control | the **RM's MCU** runs the actuator loop (reserved I/O, §5). The **supervisor** computes the target angle from sun position (GPS time and position), heading, and roll/heel from Signal K, and sends it over the existing Ethernet link. No new network |
| Stow logic | stow flat on high wind (anemometer via Signal K), when underway above a set speed [DECISION], on network loss (the RM drives to 0° on heartbeat timeout), and at night |
| Fallback | a dead actuator: unpin it and set the manual pin (§6); the tracker only ever adds harvest |

## 7. Supervisor and network

| Item | Choice |
|---|---|
| Computer | Raspberry Pi 5, industrial-temp microSD or NVMe, in a DIN enclosure, 24→5 V supply |
| CAN | 2-channel isolated CAN HAT. **CAN0** ↔ BIM Battery-Emulator board (battery protocol). **CAN1** ↔ IM bus (with IM sync pair separate) |
| Switch | **MikroTik CRS112-8P-4S-IN**: 8 ports with per-port PoE-out control from RouterOS (scriptable/API). 802.3af/at output needs a 48–57 V input, so feed it from a 24→48 V DC-DC |
| Network | the power VLAN is isolated from the boat LAN. The supervisor is the only bridge and forwards telemetry only (spec §6.2) |
| Duties | read battery limits (CAN0); set RM current limits and heartbeat (Modbus TCP); set IM limits (CAN1); night PoE-off for RMs; weekly LBC reset; load-shed; publish to Signal K and add points to `schema/points.yaml` |

**Supervisor fallbacks.** (1) A spare Pi with a cloned, versioned image (in
this repo). (2) A laptop with a USB-CAN adapter running the same software. (3)
With no supervisor at all: the IMs keep powering loads (§4.6) and the RMs
stop (fail-off), and the pack remains protected by Battery-Emulator + LBC.
Solar then goes to the house-battery path (spec §10).

## 8. Wiring schedule

| ID | From → To | Cable | Protection |
|---|---|---|---|
| W1 | panel ↔ panel | panel's own MC4 leads | — |
| W2 | string → RM input | 4 mm² PV, MC4, ≤ 3 m | RM input ratings (spec §2) |
| W3 (×2) | RM output → hold rail-feeder | **6 mm² H1Z2Z2-K** pair, ~30 m [ASSUMED; measure] | 10 A gPV at hold + isolator |
| W3F (×2) | reserved fold-out RM → hold (pulled now, capped and labeled at both ends) | 6 mm² H1Z2Z2-K pair, same route | feeder space reserved |
| W4 (×2) | RM ↔ PoE switch | Cat6 outdoor, shielded, UV | PoE port limit |
| W4F (×2) | reserved fold-out RM ↔ switch (pulled now) | Cat6 outdoor | — |
| W5 | pack HV → BIM | **25 mm² H1Z2Z2-K** pair, as short as possible | NH 40 A at the pack end |
| W6 | pack LV connector → BIM | salvaged Leaf LV pigtail → 1.5 mm² tinned + twisted pair for CAN | 5 A blade fuse on 12 V |
| W7 | busbar → IM DC in | 4 mm² H1Z2Z2-K | 20 A gPV + isolator |
| W8 | IM AC → AC test panel | 3 × 6 mm² (10 AWG) + PE, marine tinned (UL 1426 boat cable / H07RN-F) | 2-pole 20 A breaker + RCD/GFCI in panel |
| W9 | CAN1 + sync pair | shielded twisted pair (DeviceNet/NMEA 2000-type or Cat6), 120 Ω terminated | — |
| W10 | E-stop loop | 1.5 mm² tinned, NC contacts in series | fail-open by design |
| W11 | 24 V house aux → cabinet | 4 mm² tinned | 20 A breaker at house panel |
| W12 (×2) | 24 V tracker feed, hold → rail (**pulled now**, capped and labeled) | 6 mm² tinned marine duplex, ~35 m (≈4 % drop at 5 A) [DERIVED] | 10 A breaker per side in the cabinet |

Run every DC pair **together** (compass deflection, EMI, spec §8.2).

## 9. Protection coordination

| Fault location | First to act | Backup |
|---|---|---|
| Short in a rail down-run | RM (current source, ≤ 4 A) + the pack side's 10 A gPV | side isolator (manual) |
| Short on the bus in the cabinet | pack NH 40 A gPV | pack contactors via IMD/BIM |
| IM internal short | IM 20 A gPV | pack NH fuse |
| AC short | IM current-limit, then the 20 A breaker clears | IM trip at 100 ms |
| Insulation fault (bus to hull) | IMD warn → supervisor alarm | IMD trip threshold → contactors open |
| Pack cell out of limits | LBC → Battery-Emulator opens contactors | supervisor ramps IM/RM to zero first when a limit is approached |
| Everything hangs | E-stop loop: coil power cut in hardware | — |

Fuses are sized so the smallest one nearest the fault clears first (10 A /
20 A below 40 A). Confirm with the fuse maker's DC time-current curves.

## 10. Commissioning order

Each step passes before the next begins:

1. **Cabinet dry:** wiring check, E-stop loop, IMD self-test, no pack connected.
2. **BIM + pack, no load:** wake, read LBC, precharge onto the empty bus, close,
   open. Log the precharge time. Pull the E-stop in every state.
3. **IM on a bench HV supply** (not the pack): DCX, then bridge, then a
   resistive load, then surge, then every protection injected (spec P1
   principle: the right trip fires).
4. **IM on the pack:** resistive load to 3.5 kVA; an hour at full load; thermal survey.
5. **Second IM:** parallel, sharing within 10 %; pull the sync pair (droop
   takes over), pull CAN, pull the master.
6. **RMs on the bench** (spec P0–P1), then on the rail (P2), then into the pack.
7. **Full chain:** sun → RM → bus → pack → IM → loads for a week; fallback
   drills (spec P5).

## 11. Open items (Phase 1)

1. Panel datasheet (Voc, Isc, max system voltage); spec §12.1 still blocks the 4S future.
2. Leaf internal precharge resistor value vs. total bus capacitance (§3.2).
3. Leaf pack weight and dimensions in hand (§3.3); LV connector pinout on
   this pack (confirm against Battery-Emulator's Leaf wiki).
4. Fire, ventilation and detection plan for the battery space (ABYC E-13).
5. Transfer switching between shore/genset and the IM AC output; where Phase
   1's AC panel ties in (not to the 440 V bus).
6. Insurer notification: no NRTL on panels or custom modules; solar cable, not boat cable.
7. Tracker mechanical spec (Phase 2); it must carry the fold-out geometry of §6.1.
8. Fold-out wind and hinge loads, and the deployed-weather limit, once the panel is chosen.
9. Tracker travel: ±60° linear actuator vs ±90° slew drive (§6.2); actuator sizing once panel mass and the fold-out loads are known.
