# Eris software BMS

Software battery management for the three 24 V starting banks (main port,
main starboard, shared generator bank; each 2×12 V truck batteries in
series). Chemistry assumed flooded lead-acid — confirm; the SoC model
depends on it.

This is a *monitoring and judgment* layer, not a protection layer. Lead-acid
starting banks need no cell balancer; they need someone noticing decline
before a no-crank morning. That someone is this software.

## What it computes, per bank

| Output | Method | Needs |
|---|---|---|
| State of charge | Rested open-circuit voltage table (lead-acid OCV↔SoC is reliable after ≥4 h rest) + coulomb counting between rests when a shunt exists | voltage (have planned); shunt (candidate) |
| **State of health** | **Cranking-sag capture**: sample voltage at ≥10 Hz during each start event, extract minimum sag and recovery time, trend across events. A widening sag at constant temperature is the death signal | voltage at 10 Hz during cranking (event-triggered) |
| Series imbalance | Midpoint voltage: the 12 V tap between the two series batteries. Divergence from V/2 means one battery is failing while the pair still reads a healthy 24 | midpoint tap per bank (cheap, high value) |
| Charge verification | After each start: alternator raises bank to absorption within expected time; at dock: charger profile sanity | voltage + engine state (have) |

## Alarm rules (initial)

- `LOW_VOLTS`: rested bank < 24.4 V (≈70 % SoC for flooded) — warn; < 23.8 — alarm
- `SAG_TREND`: cranking minimum degraded > 0.8 V vs 90-day baseline at similar temp — service advisory
- `IMBALANCE`: |midpoint − V/2| > 0.35 V sustained — one battery of the pair is failing
- `CHARGE_FAIL`: engine running > 5 min and bank < 26 V — alternator/regulator problem
- `SHARED_BANK`: any alarm on the generator bank is flagged double-severity — it threatens both gensets at once (schema topology)

Thresholds are starting points from flooded lead-acid practice, to be tuned
against this boat's own history once VictoriaMetrics has a season of data.

## Integration

- Inputs arrive as Signal K deltas (`electrical.dc.startBanks.*`)
- `bms.py` evaluates on every delta; publishes derived paths
  (`...soc`, `...health.crankingSagV`, `...alarms`)
- History: VM remote-write; the sag trend query is a VM range query
- The cranking capture is edge work: the sensing node must buffer 10 Hz
  locally on start detection (fuel solenoid TRUE is the trigger — already a
  schema point) and ship the event as a batch

## Hardware this implies (per bank)

1. Voltage sense: bank + **midpoint tap** (6 channels total for 3 banks)
2. Optional shunt for coulomb counting (banks are start-only; SoC from OCV
   may suffice — decide after a month of voltage data)
3. Temperature: one sensor per battery box (sag thresholds are temp-relative)

Nothing here requires committing to N2K vs ESP32 yet; a $5 ADC per bank
covers the voltage channels either way.
