# Phase 1: pricing summary

Prices were seen **2026-09-22** and are merged line by line into
`phase1-bom.csv` (columns `usd_low`, `usd_high`, `price_basis`,
`price_source`). Each price has a basis:
- **QUOTE**: a listing page that was actually loaded.
- **SNIPPET**: search-result text only. Confirm before buying.
- **EST (research) / EST (mine)**: estimates, not quotes.

Shipping, tariffs, distributor minimums and currency movement are not
included. Conversions assumed €1 = $1.15 and NZ$1 = $0.58.

## Totals (USD)

| Assembly | Low | High | What sets the range |
|---|---|---|---|
| Rail (4 panels, frames, detachable hardware, 2 deck boxes) | 3,461 | 7,351 | deck boxes ($1.2–3k, fabricated) and 316 SS vs galvanized strut |
| Down-runs (2 pairs + 2 Cat6 per side, tracker 24 V feed) | 1,070 | 1,302 | |
| Rail modules (3 built) | 1,624 | 2,049 | enclosure size, PCB fab |
| Hold cabinet | 2,430 | 3,372 | generic vs branded fuse holders; the insulation monitor alone is $978 |
| BIM, **including the Leaf pack** | 5,491 | 12,965 | the pack: $4,450–10,600 with freight |
| Inverter modules (2 built) | 2,417 | 3,115 | |
| Supervisor + network | 839 | 1,128 | |
| AC test panel | 473 | 778 | |
| Spares | 272 | 333 | |
| **Phase 1 total** | **~18,100** | **~32,400** | |
| of which the Leaf pack | 4,450 | 10,600 | |
| **Phase 1 without the pack** | **~13,600** | **~21,800** | |
| Test gear the owner doesn't already have | 0 | ~5,000 | see below |

## Test equipment: check against your bench

Minimum ratings (BOM T01–T10). The lab notes in `casimir_research` show a
500 MHz+ scope, 6.5-digit DMM and function generator. The 0–60 V Sorensen
DCS60-18E appears there as equipment you'd supply, so it may not be on hand.
If you have it, it can stand in for the Phase 1 **2S** string (Voc ≈ 49 V,
Vmp 41.5 V). A 4S string needs ~110 V.

| Line | Need | Why | Usually on an optics bench? |
|---|---|---|---|
| T01 | DC supply ≥ 150 V, ≥ 10 A (PV simulator) | RM bench (4S later) | 60 V covers Phase 1 2S only |
| T02 | **DC supply ≥ 450 V, ≥ 2 A, current-limited** | IM bench before the pack | rarely |
| T03 | **Electronic load ≥ 500 V DC, ≥ 1 kW** | RM output, IM bench | rarely |
| T04 | Scope 4-ch ≥ 200 MHz | everything | yes |
| T05 | **HV differential probes ≥ 1.5 kV, ×2** | floating switch nodes; never ground-clip a floating HV node | rarely |
| T06 | AC/DC current probe, ≥ 1 MHz | inductor and switch currents | sometimes |
| T07 | Multimeter CAT III 1000 V / CAT IV 600 V | the pack and the bus | a bench DMM isn't a CAT-rated handheld |
| T08 | **Insulation tester 1000 V** | cables, array, IMD check | rarely |
| T09 | **Class 0 gloves + leather protectors** | 400 V DC work | rarely |
| T10 | LOTO kit + arc face shield | pack work | rarely |

Budget options if missing: ETOMMENS eTM-6002 600 V/2 A ($699), Maynuo
M9714B 500 V/1.2 kW (~$1,070), 2× Micsig DP1500 ($710), Klein ET600 ($184),
Salisbury GK011R ($165). Sources are in the BOM.

## Buy now (availability)

1. **LAUNCHXL-F280039C ×5**: out of stock at TI, Digi-Key and LCSC. Mouser
   had ~43 (snippet). If they're gone, switch both designs to
   LAUNCHXL-F280049C (in stock; needs a firmware port, since it's a different part).
2. **IPP110N20N3 G ×24**: Digi-Key shows 20. Split the order with Mouser/LCSC.
3. **C3D10065A** (52-week standard lead) and **C3M0075120D** (20-week): stock
   exists today; buy with spares.
4. **Omron G2RG-2A-X DC12** (RM output relay, IM precharge): 0 stock, 62
   due Oct 14. Check its coil power against the RM's 13 W PoE budget.
5. **Leaf pack:** the market is thin, and none turned up in Indonesia. Ask any
   seller for a LeafSpy state-of-health screenshot, the LV and HV pigtails
   from the donor car, and its weight (315–366 kg reported). Ships as Class 9
   (UN3480) freight.

## Corrections the pricing pass made to the BOM

- C13: **Mean Well SD-100B-48 does not exist** → DDR-120B-48 (48 V is at the
  bottom of the switch's 48–57 V PoE input; check the output trim).
- I04: MGJ2 has no +15/−4 V version → **+15/−5 V** (MGJ2D121505SC). That is
  within the SiC gate's −8 V limit, but check the C3M0075120D datasheet's
  recommended off-voltage.
- D02: the cheapest outdoor Cat6 is **copper-clad aluminium**; the spec now
  requires solid copper.
- D01/B09: US PV wire sizes run small (10 AWG = 5.3 mm², 4 AWG = 21 mm²).
  Buy metric H1Z2Z2-K or go one AWG size up.
- A03: a US split-phase GFCI breaker needs its own load centre, so it's replaced
  by an **IEC 4-pole 30 mA RCD** (DIN, sold worldwide) with L1, L2 and N through it.
- A04: split-phase + ground needs **4 conductors**; 10/3 triplex + one green.
- S06: the priced PoE injectors run on mains AC; the fallback needs
  **DC-input** injectors fed from the 48 V rail.
- C10: the **Bender IR155-3204** may be discontinued in the US and was the
  only price found ($978). Ask Bender about the iso165C, or find an alternative.
- M16/M17/M18/M09/I14: substitutes recorded in the BOM (INA240A2, MEJ2S1205SC,
  Omron G2RG, TDK N97 ETD39, cheaper EV contactors).

## What these prices don't cover

- The two PCB designs (schematic + layout) and firmware: that's labour.
- Tracker actuators (later), fold-out panels and their RMs (later).
- Marine-surveyor or insurer requirements (open item).
