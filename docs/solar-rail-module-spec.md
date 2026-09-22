# Solar rail module: specification, draft 0.1

The rail module is the power converter that takes one group of four solar
panels on a rail tracker and pushes their power down a shared ~350 V DC bus
into the Leaf-module battery in the hold (two strings of 24 modules, 80 kWh). Six identical modules, three per side.
It is programmable, networked, and powered and enabled over PoE.

This is a design spec, not a record of built hardware. Following this repo's
"nothing invented" rule, every number carries its source:

- **[MAKER]**: the panel maker's published figures (Newpowa NPA200S-12J-Bi), not independently verified
- **[ASSUMED]**: a typical value, standing in until the real one is known; listed in *Open items*
- **[DERIVED]**: computed from the above; changes if they change
- **[DECISION]**: a design choice, open to revision by the owner

## 1. System context

```
PORT TRACKER (12 panels)                       HOLD
 [4S]->[RM-P1]--+                              +----------------------------+
 [4S]->[RM-P2]--+==== 350 V DC, port run ====> | DC combiner: fuse/module   |
 [4S]->[RM-P3]--+                              | bus disconnect             |
                                               | insulation monitor         |
STARBOARD TRACKER (12 panels)                  |        |                   |
 [4S]->[RM-S1]--+                              | string contactors+precharge|
 [4S]->[RM-S2]--+==== 350 V DC, stbd run ====> |        |                   |
 [4S]->[RM-S3]--+                              | 2 strings x 96S2P, 80 kWh  |
                                               |                            |
 all RMs <======== Ethernet + PoE ===========> | PoE switch -> supervisor   |
                                               | supervisor <-CAN-> 2 BMSs  |
                                               +----------------------------+
```

- **The pack is the bus.** No inverter, no AC, no bus-forming converter. The
  bus voltage is whatever the pack is at.
- **Each rail module (RM) is a current source into the bus.** It never
  regulates bus voltage, except for the backup ceiling in section 6.3.
- **Port and starboard never share a series string.** They are on different
  trackers, see different sun, and the deckhouse shades each side differently.
- Out of scope here, but specified as interfaces: the hold-side combiner,
  the pack contactor/precharge chain, the supervisor, and the load side
  (the pack feeding ship's loads).

## 2. Input: four panels in series

**Panel: Newpowa NPA200S-12J-Bi** (200 W, 12 V-class mono, **bifacial**),
chosen 2026-09-22 in place of the original WERCHTAY listing, which had no
datasheet. Owner prefers bifacial. It fits the ~55 in rail bay: 1370 mm
long, leaving ~27 mm (1 in) of clearance, so **measure the posts**; 765 mm
tall, so the rail caps sit ~2.1 in above 28 in.

| Quantity | Per panel | 4S string | Source |
|---|---|---|---|
| Rated power (STC) | 200 W | 800 W | [MAKER] |
| Vmp / Imp (STC) | 20.74 V / 9.68 A | 83.0 V / 9.68 A | [MAKER] |
| Voc / Isc (STC) | 24.34 V / 10.31 A | 97.4 V / 10.31 A | [MAKER] |
| Temp. coeff. Pmax / Voc | −0.38 / −0.36 %/K | | [MAKER] |
| Voc at −10 °C cell | | **109.6 V** | [DERIVED] +12.6 % |
| Vmp at −10 °C / 70 °C cell | | ~94 V / ~69 V | [DERIVED; Vmp coeff ASSUMED ≈ Pmax coeff] |
| Max system voltage | 1000 V | | [MAKER] |
| Rear side | bifacial, transparent backsheet (not dual glass); rear gain **not published** | | [MAKER] |
| Isc with rear gain | ~12.4 A at +20 % rear gain | | [ASSUMED] 20 % rear gain, generous for a rail mount over water and deck |
| Size / weight | 1370 × 765 × 35 mm / ~11 kg | | [MAKER] size; weight [ASSUMED] from the mono NPA200S-12J (11.2 kg), not published |
| Efficiency | 19.1 % front | | [DERIVED] 200 W / 1.048 m². Newpowa's "21.8 %" presumably counts rear gain |
| Certifications | **none found** (no UL/IEC certificate numbers, no IEC 61701 salt mist) | | ask the seller before buying; seal junction boxes (§8) |

[MAKER] = the maker's published figures (newpowa.com), not independently
verified. Measure one panel in P2 (§11).

### Input ratings [DECISION]

| Parameter | Value | Why |
|---|---|---|
| Absolute max input voltage | **150 V** | 37 % margin over the 4S cold Voc (109.6 V). 5S (137 V cold) would also be inside it, but its cold Vmp (~117 V) leaves the MPPT window |
| MPPT window | **30–110 V** | a 4S string from hot and dim (~69 V) to cold Vmp (~94 V), **plus degraded 3S and 2S strings** with dead panels bypassed (section 10); full power only for 4S |
| Max input current, continuous | **18 A** | NPA200S-12J-Bi with +20 % rear gain needs ~15.5 A (Isc × 1.2 × 1.25, NEC 690.8 practice for irradiance enhancement); 18 A covers it |
| Rated input power | **1.1 kW** | 800 W nameplate + margin (the board was rated before the panel was chosen; it stays, so a stronger panel fits without a redesign) |
| Reverse-polarity protection | required, non-destructive | miswiring at the rail is likely |

## 3. Output: the pack bus

| Quantity | Value | Source |
|---|---|---|
| Battery configuration | 2 strings in parallel, each 24 Leaf Gen 3 modules (4S2P) in series = 96S2P, 40 kWh; 80 kWh total | Phase 1 LLD §3 |
| Pack voltage range | 288–403 V (3.0–4.2 V/cell) | [DERIVED] from 96S NMC |
| Nominal | ~350 V | [DERIVED] 96 × 3.65 V |
| **Operating output range** | **250–420 V** | [DECISION] margin both ends |
| Absolute max output | 450 V | [DECISION] |
| Max output current | **4.0 A** | [DERIVED] 1.1 kW × 0.96 / 288 V = 3.7 A, rounded up |
| Reverse current | **zero, blocked** | the pack must never back-feed a module |

Six modules at full sun put ~14 A into the pack (4.8 kW nameplate at
~350 V), under 0.1C for the 80 kWh battery, well within Leaf charge ratings. Each
side's run normally carries ~7 A; it is fused and rated for the modules'
4 A maximum each (≤ 12 A per side).

## 4. Power stage

The difficulty is the voltage ratio. From a 4S string, the converter goes from
~69 V to 403 V (5.9:1) at worst and from ~94 V to 288 V (3.1:1) at best. The
module needs a transformer anyway, for galvanic isolation (section 7). Two
candidate topologies:

### Option A: boost + LLC DC transformer, two stages [RECOMMENDED for the first build]

```
PV 30-110 V -> [sync boost, MPPT, current-mode] -> V_int -> [LLC at resonance, 1:2.8, fixed ratio] -> bus 288-403 V
```

- The LLC runs **unregulated at its resonant frequency**, as a DC transformer
  (DCX), where it is ~97–98 % efficient and has zero-voltage switching
  across the full load range. The intermediate voltage just follows the
  bus: V_int = V_bus / 2.8 = **103–144 V**.
- The boost does all the regulation: MPPT and output current limit. Its
  output (103 V minimum) is always above the highest string Vmp (~94 V on a
  cold morning), so it never has to step down. [DERIVED] The ratio is
  1:2.8 rather than 1:3 for exactly this margin: at 1:3 the floor
  (96 V) would sit only 2 V above the cold Vmp.
- Device voltages: boost switches in the 200 V class, LLC primary in the
  200 V class, secondary rectifier in the 650 V class (GaN or SiC).
- Expected efficiency: ~95–96 % overall. [ASSUMED from typical stage efficiencies]
- Why first: each stage is textbook and can be debugged on its own. The
  LLC-DCX can be bench-tested first with a plain DC supply.
- Reverse blocking: diode rectification on the secondary, or synchronous
  rectification with its gate drive held off whenever V_int would be lower
  than V_bus / n.

### Option B: single-stage dual active bridge (DAB)

- One transformer with a full bridge on each side, controlled by phase
  shift. Needs triple-phase-shift or similar modulation to keep zero-voltage
  switching across a 2.9–6.2:1 gain range.
- Fewer magnetics and possibly ~1 % more efficient. The control is much harder,
  and light-load efficiency suffers when the gain is far from the turns ratio.
- Worth building as revision 2 once Option A works.

### Common power-stage requirements

- Switching frequency, magnetics and layout: [DECISION], to be set during design.
- Input and output capacitors rated for 105 °C ambient inside the enclosure.
- **Output precharge:** before closing onto a live 350 V bus, the module
  charges its own output capacitors to within 5 V of the bus from its own
  converter, then closes its output relay at zero current.
- Output relay: DC-rated, ≥ 450 V, opened and closed only at zero current.

## 5. Control

### 5.1 Current command

On every control cycle, the output current command is the **minimum** of:

1. **MPPT**: perturb-and-observe or incremental conductance on input power.
   Tracking period ~100 ms. Rolling on the rail changes irradiance on second
   timescales, so the MPPT must follow a moving target, not just a slow sun.
2. **Network limit**: the supervisor's current limit for this module
   (section 6.2). **Default is zero.**
3. **Local hard limit**: 4.0 A, set in firmware and backed up by hardware
   overcurrent protection. The network cannot raise it.
4. **Bus-voltage ceiling**: a backup that doesn't depend on the network (section 6.3).
5. **Thermal derate**: linear from 70 °C to 85 °C heatsink temperature, then off.

"Minimum of the limits" is the safety principle: every limit can only
**reduce** power. Nothing on the network can command more than the module's
local limits.

### 5.2 Controller [DECISION]

- A real-time MCU for the power loops. TI C2000 class (e.g. F28003x or F28P65x)
  has the high-resolution PWM, fast ADCs and CAN, plus mature LLC and boost
  reference code.
- Ethernet: either on the MCU or a small sidecar (e.g. W5500 or an
  Ethernet-capable MCU) linked to the loop MCU over SPI. The power loop must
  not depend on the network stack's timing.
- Signed firmware images with A/B slots; see sections 6.2 and 10.

### 5.3 Bench constant-voltage mode (bench use only) [DECISION]

A proven RM doubles as the bench **high-voltage source** for bringing up the
inverter modules (Phase 1 LLD §10). No separate HV supply is bought.

- **What it does:** regulates its *output voltage* to a setpoint (250–420 V)
  instead of tracking MPP. The current limit is the module's local limit
  (4 A) and the input supply's CC setting (2× Sorensen DCS60-18E in
  series, 120 V / 18 A). Capacity is ~1 kW.
- **Output stiffness:** an external capacitor bank (≥ 100 µF, ≥ 500 V, with a
  **bleeder** that takes it below 50 V within 60 s) at the output terminals.
- **Enable:** only with the **bench jumper** fitted *and* the bench-mode
  config bit set. With the jumper fitted, the module refuses the
  supervisor's heartbeat and Modbus writes, so it **cannot join the
  vessel's bus**. The supervisor, in turn, alarms on and ignores any module
  reporting bench mode. Aboard, the jumper is not fitted.
- **Heartbeat:** replaced by the local enable (the jumper plus a bench
  enable switch). PoE still powers gate drive, from a bench PoE injector,
  so pulling PoE still stops it.
- **Protections:** unchanged (section 7). Output OV stays at 425 V.

## 6. Network, PoE and protocol

### 6.1 PoE

| Parameter | Value |
|---|---|
| Standard | IEEE 802.3af, Class 3 (≤ 12.95 W at the powered device) is sufficient; 802.3at allowed |
| Loads on PoE | MCU, sensing, **all gate drivers**, relays, fan if any |
| Loads NOT on PoE | the power path itself |
| Entry | cable gland (M20/PG) into the enclosure, terminated on an internal RJ45 jack; no special connectors (section 8.1) |
| Isolation | the 1500 V isolation 802.3 requires is kept |

**PoE as a hardware enable.** Gate-drive power comes only from PoE. If PoE is
lost, the drivers lose power and the converter stops, whatever the firmware is
doing. A cut cable, a dead switch or a supervisor that turns the port off all
stop the module the same way. No module can put power on the bus without a
live link from the hold. That is the DC equivalent of rapid shutdown.

**Night standby cost.** Six modules at ~3 W each is ~18 W, or ~430 Wh/day,
up to ~2 % of a good day's harvest. The supervisor should turn off PoE
ports after sunset and back on at dawn. [DECISION] The switch must support
per-port PoE control from the supervisor.

### 6.2 Protocol [DECISION: proposed]

- **Modbus TCP** for configuration and telemetry: simple, standard, and
  tooling exists everywhere.
- **Heartbeat/limit frame**: the supervisor writes the current limit and an
  incrementing sequence number at 10 Hz. If the module sees no new sequence
  number for **500 ms**, it ramps its output to zero within 100 ms and stays
  there until heartbeats resume for 2 s.
- The supervisor publishes module telemetry to Signal K under
  `electrical.solar.<id>.*` (check path names against the Signal K spec) and
  adds the points to `schema/points.yaml`, the twin's point contract.

**Security (default-deny).** Modbus has no authentication, so:
- The power network is a **physically separate switch and VLAN**, with no
  route to the boat LAN, Wi-Fi or LTE. The supervisor is the only bridge, and
  it only forwards telemetry outward.
- The module accepts writes only from the supervisor's address. Even so, the
  worst a forged write can do is *lower* current (section 5.1), never raise it
  past the local limits.
- Firmware updates: signed images, verified by the bootloader, on the
  isolated network only.

Draft register map:

| Reg | Name | R/W | Units |
|---|---|---|---|
| 0 | heartbeat_seq | W | counter |
| 1 | i_limit_cmd | W | mA, clamped to local limit |
| 2 | enable | W | 0/1 |
| 10 | v_in | R | 10 mV |
| 11 | i_in | R | mA |
| 12 | v_out (bus) | R | 100 mV |
| 13 | i_out | R | mA |
| 14 | p_in | R | W |
| 15 | state | R | enum: OFF, WAIT_PV, PRECHARGE, MPPT, LIMITED, FAULT |
| 16 | limit_reason | R | enum: MPPT, NET, LOCAL, VBUS, THERMAL |
| 17 | fault_bits | R | bitfield (section 7) |
| 18–20 | t_heatsink, t_magnetics, t_enclosure | R | 0.1 °C |
| 21 | array_insulation_kohm | R | kΩ (section 7) |
| 22–23 | energy_wh | R | uint32 |
| 30–39 | config (droop points, derate) | R/W | writes only accepted with enable = 0 |

### 6.3 Bus-voltage ceiling (works with the network down)

The module reduces current linearly from **V_start = 398 V** (4.146 V/cell
average) to zero at **V_stop = 401 V** (4.177 V/cell). [DECISION] Configurable.

**This is a backstop, not charge control.** Bus voltage is the pack
*average*. A high cell can reach 4.2 V while the average is lower. Real
charge termination comes from each string BMS's per-cell data,
passed through the supervisor as the network limit (section 5.1, item 2).

## 7. Protection and fault handling

| Fault | Detection | Action |
|---|---|---|
| Input overvoltage | V_in > 140 V | stop, latch |
| Input reverse polarity | hardware | blocked, no damage |
| Array insulation fault | array-to-chassis insulation resistance measured before each start (the array floats; see below) | below threshold: refuse to start, report |
| Output overvoltage | V_out > 425 V | stop, open relay, latch |
| Output overcurrent / short | hardware comparator, < 10 µs | stop switching |
| Reverse current | V_out > V_int·n or reverse current seen | blocked by rectifier; relay opens |
| Overtemperature | NTCs on heatsink, magnetics, enclosure | derate, then stop |
| Heartbeat lost | 500 ms timeout | ramp to zero (section 6.2) |
| PoE lost | hardware | gate drivers lose power, stop |
| DC series arc | **Phase 2**: arc detection from input/output current spectrum (UL 1699B concept) | stop, latch |

**Isolation and grounding.** Transformer isolation keeps the PV array floating
and galvanically separate from the pack and the bus. Design target: the
insulation coordination of IEC 62109-1 for PV power converters (values TBD
during design). A floating array lets the module measure the array's
insulation resistance before every start. Salt-spray leakage then shows up as
a falling trend in the telemetry, long before it becomes a fault.

## 8. Mechanical and environmental

- **Location:** at the rail base, on fixed structure, **not on the moving
  tracker**. Only the PV leads cross the tracker's rotating joint (in a
  service loop or cable chain).
- Enclosure: IP67, anodized aluminium or 316 stainless, UV-stable gaskets.
  The heatsink is outside the seal; sealed units run fanless.
- Salt mist: design to IEC 60068-2-52; conformally coat all PCBs.
- Ambient at the rail: −10 °C to +60 °C [ASSUMED]; full power up to 50 °C.
- Vibration, shock and EMC: IEC 60945 (marine equipment) as the reference
  test set; the boat has radar and VHF nearby, so keep radiated emissions
  low (the soft-switching LLC helps).
- PV input: MC4 connectors.
- Bus output: **no connector.** The bus cable comes in through a cable gland
  to a DIN-rail terminal block inside. With no plug on the bus side, the
  350 V bus can never be mated into the 150 V PV input by mistake.

### 8.1 Sourcing rule: fixable in any port

The boat will be far from a supplier. **Every part outside the module's PCB
must be something a solar installer or electrical wholesaler stocks
worldwide** (anywhere rooftop solar is sold, which includes Indonesia and
most of SE Asia and the Pacific):

| Item | Use | Why it is everywhere |
|---|---|---|
| PV cable EN 50618 **H1Z2Z2-K**, 6 mm² (or UL 4703 PV wire, 10 AWG) | DC bus runs, PV leads | the standard rooftop solar cable |
| MC4 connectors + crimp tool | PV strings | universal on panels |
| gPV fuses 10×38 mm, 1000 VDC, + DIN fuse holders | combiner | standard in every solar combiner box |
| DC isolator / disconnect, 1000 VDC, DIN or enclosure-mount | per side, at the pack | standard solar string isolator |
| Cat6 outdoor (UV jacket, shielded) + RJ45 | PoE/Ethernet | commodity |
| Nylon cable glands (M/PG series), DIN rail, terminal blocks | enclosure entries | commodity |
| Off-the-shelf PoE switch with per-port control (managed, 802.3af/at) | hold | commodity |

**The module itself is custom, so the spare is a whole module.** Build
**8 modules for 6 positions**, carry 2 spare modules plus a bag of the
parts that die first (MOSFETs, gate drivers, fuses, one MCU board). A
failed module swaps out in minutes with a screwdriver and the terminal
block. You don't repair the power stage at sea. Buy spares of any
long-lead parts (transformer cores, litz wire, the MCU) when building,
not when they fail.

**Fallback if the modules all fail:** each side's 12 panels still have MC4
leads, so any off-the-shelf MPPT charger that fits the panels can charge
a 12/24 V house battery directly. It doesn't help the Leaf battery, but
you get limping power from parts sold anywhere. [DECISION: owner to
confirm this is wanted]

### 8.2 DC bus cable

| Parameter | Value | Source |
|---|---|---|
| Cable | **H1Z2Z2-K 6 mm², single core, red + black**, tinned copper, 1.5 kV DC, UV/ozone rated | [DECISION] EN 50618 |
| Run | one pair per side, from the rail combiner point to the hold combiner | |
| Current per side | ≤ 12 A (3 modules × 4 A) | [DERIVED] |
| Drop, 30 m run (60 m loop) | 60 m × 3.39 mΩ/m = 0.20 Ω → 2.4 V (0.7 %), ~29 W at full sun | [DERIVED; run length ASSUMED, measure it] |
| Protection | 20 A gPV fuse **at the pack end** of each side run, plus 6 A gPV per module | [DECISION] the pack can deliver thousands of amps into a fault; the fuse at the source end protects the run |

- 4 mm² would work electrically (1 % drop). 6 mm² is chosen for mechanical
  strength, chafe margin and headroom, and the price difference is trivial.
- **Run + and − together** (bundled, or twisted every ~300 mm). Separate runs
  make a current loop that can **deflect the magnetic compass** and radiate
  into radar and VHF.
- Keep the run off fuel lines and out of bilges. Support it every ~450 mm
  (ABYC practice). Use chafe sleeve and glands at every bulkhead and deck
  penetration. Label it "350 V DC" at every access point.
- EN 50618 is a solar-industry cable, not a marine-listed one. It is tinned
  and UV- and ozone-rated, which covers most of what marine cable is for.
  But it is **not ABYC/UL 1426 boat cable**. That goes on the insurer list
  (section 12, item 3).

## 9. Hold-side interface (defined here, specified separately)

- **Combiner:** one fuse per module (gPV class, ≥ 600 VDC, ~6 A) and one
  DC-rated disconnect per side.
- **Bus insulation monitor** on the 350 V bus relative to hull.
- **String contactors and precharge**, one set per string, driven by that
  string's BMS (Phase 1 LLD §3.3). Build and test this interlock chain
  before any rail module connects to the battery.
- **Supervisor:** reads both string BMSs over CAN, computes rail-module
  current limits from the lower of their charge limits and the cell data,
  runs the heartbeat, switches PoE ports, and publishes to Signal K.
- Relation to `software/bms/`: that code covers the 24 V lead-acid starting
  banks. The solar/battery supervisor is a separate program. They can share
  the Signal K integration pattern.

## 10. Fallback paths

Design rule: **no single failure should leave the boat without solar
charging, if a fallback is practicable. Where it isn't, the failure must
leave the system safe (off), not half-working.** Each fallback uses only
section 8.1 parts or equipment already aboard.

| What fails | Effect | Fallback | Needs |
|---|---|---|---|
| One panel | its 4S string is down | bypass the dead panel with an MC4 jumper; the module runs the 3S string (MPPT window goes down to 30 V) at ~¾ power; a 2S string also runs, at reduced power | a spare MC4 jumper per side |
| One rail module | 1/6 of the array is down | swap in a spare module (screwdriver, terminal block); until then the other five keep running | 2 spare modules (section 8.1) |
| One side's bus cable or fuse | that side is down | isolate that side at its disconnect; the other side keeps charging; repair with stock PV cable and MC4/terminal parts | each side independently fused and isolated (section 8.2) |
| One tracker drive | that side can't track | pin the tracker flat (0°, which is also the stow position) and run fixed; expect roughly 20–30 % less from that side [ASSUMED] | manual lock pin on each tracker |
| PoE switch | all modules stop (by design) | swap in a spare managed PoE switch, or use **single-port PoE injectors** (commodity) on any switch, one per module | 1 spare switch or 6 injectors |
| Supervisor computer | heartbeats stop, all modules ramp to zero (safe) | boot the **spare supervisor**: identical SD card image or disk, on a spare board, or on a laptop with a USB-CAN adapter (the image must run on commodity hardware) | spare board + image, versioned in this repo |
| One string's BMS or its CAN link | no per-cell data for that string | that string's contactors open; **the other string carries on** at half capacity with halved limits. A string is never charged without cell monitoring | two independent BMSs |
| Whole converter system (all modules, supervisor, or both strings) | no charging into the Leaf battery | **house-battery path:** the MC4 panel leads go to any off-the-shelf MPPT charger (12/24/48 V, sold everywhere) charging a lead-acid or LiFePO4 house battery. The input window per string is still 4S | one stock MPPT charger aboard, pre-wired to a changeover point |
| One Leaf module | its string trips | swap in a spare module (carried aboard). Degraded mode: rebuild the string at 23 modules (92S: 276–386 V, inside the converters' 250–420 V range) with the BMS reconfigured | spare modules; configurable BMS (Phase 1 LLD §3.6) |
| Network with a working supervisor (e.g. a flaky link to one module) | that module stops (heartbeat timeout) | the others continue; the supervisor logs which module keeps timing out | — |
| Module firmware bug in the field | module misbehaves | every module keeps a **known-good firmware image** alongside the update slot, and the bootloader falls back to it; a physical jumper forces it | A/B firmware slots |

**What deliberately has no fallback:** anything that would charge a Leaf
string without cell-level monitoring, or let a module run without a live
link from the hold. Those are the protections. Bypassing them is not a
fallback.

## 11. Build and test plan

| Phase | Setup | Pass criteria |
|---|---|---|
| P0 | LLC-DCX alone: DC supply in, resistive load out, **reduced voltage first** (e.g. 30 V in) | ratio holds 1:2.8 under load; ZVS confirmed on scope; efficiency ≥ 96 % at full voltage |
| P1 | Full module: PV simulator (2× Sorensen DCS60-18E in series, with a series resistor for a sloped I-V curve) in, DIY water-heater load bank out | MPPT tracks ≥ 99 % of simulator MPP; every section-7 fault fires when injected, **and the right one fires** |
| P1b | Bench CV mode (section 5.3): capacitor bank + bleeder on the output, load bank stepped | output holds setpoint ±1 % from 0 to 1 kW; the bench jumper blocks heartbeat and Modbus writes; pulling PoE stops it |
| P2 | One module on 4 real panels, into a bench HV load | real Voc/Isc/Vmp logged, replacing every [ASSUMED] in section 2 |
| P3 | Supervisor + one module + one Leaf string, with contactors | PoE loss, heartbeat loss and cable pull each stop output within spec |
| P4 | All six modules | per-side harvest logged; night PoE cut works; a week of insulation trend |
| P5 | Fallback drills | each section-10 fallback done once for real (panel bypass, module swap, side isolation, injector swap, spare supervisor boot, house-battery changeover), with the time it took written down |

Every protection has to be driven to fire deliberately in P1. A protection
never seen to fire isn't verified.

## 12. Open items

1. **Panel datasheet:** Voc, Isc, temperature coefficients and **maximum
   system voltage**. If the maximum system voltage really is 30 V, series
   strings are impossible and this spec's input section fails. Measure a
   panel (P2) regardless.
2. **Real panel power:** measure one NPA200S-12J-Bi against its published figures, and the rear gain as mounted on the rail.
3. **No NRTL listing** on the panels, and none on these custom modules. **Tell
   the insurer** before installing (policy docs are in `yacht/`).
4. **Tracker mechanics:** axis orientation, ±90° drive, stow position and
   wind limit, green-water loading on the rail. That's a separate spec.
5. **Leaf battery interface:** see Phase 1 LLD §3 (two strings, BMS
   choice, module compression, rack thermal design).
6. **Fire and ventilation plan** for 80 kWh of NMC in the hold (ABYC E-13).
7. **Load side:** how the pack feeds ship's loads (the 440 V delta bus or
   something else). Independent of this spec.
