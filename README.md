# eris
M/Y Eris: a Point-class cutter conversion, and her digital twin.

Prototype Dashboard for Main Engines
![image](https://user-images.githubusercontent.com/14135501/223915028-afd521f9-b094-454e-b7cc-ff969969869d.png)

---

# Digital twin

Digital twin of *Eris*, an 82-foot ex-USCG Point-class cutter. This repo is the twin's source of truth: geometry, asset structure, telemetry schema,
process models, and (eventually) the live data pipeline.

## What exists today

| Layer | Artifact | State |
|---|---|---|
| Geometry | `drawings/` — USCGC Point Barnes drawing set (sister ship): hull lines, inboard/outboard profiles, decks. Previews here; full-resolution TIFs (up to 12360×9483) stay in `Downloads\Uscg-point-barnes.zip` | scanned, not yet digitized |
| Asset structure | `schema/marinedata_postgres.sql` (was `MarineData.txt`) — Postgres schema with SFI code classification, equipment categories | drafted (from `yacht/MarineData.txt.txt`) |
| Telemetry points | `schema/points.yaml` — engines, gensets, ER fans, formalized from the hand list in `yacht/data-model.txt` | v0.1, gaps listed in-file |
| Process models | `process/fuel_polishing_bpmn.xml` — fuel polishing procedure (100µm → 30µm → 10µm) | done |
| Reference docs | `yacht/` — Twin Disc HP9400/HP10500 manuals, Detroit 2-71 parts notes, anchor templates, insurance | in place, not mirrored here |
| STEP standards | `yacht/ISO10303/` — AP216 (moulded forms), AP218 (ship structures), AP227 (plant spatial) schema sets | collected Jan 2025 |

## Architecture (proposed)

```
                      ┌──────────────────────────────────────────────┐
   sensors (N2K,      │  Signal K server (aboard)                    │
   analog via ESP32/  │   - live state, standard marine paths        │
   SeaTalk, engine    │   - schema/points.yaml = the point contract  │
   senders)      ───► │                                              │
                      └───────┬──────────────────────────┬───────────┘
                              │ remote-write (LTE/hermes)│ websocket
                              ▼                          ▼
                      VictoriaMetrics (Atlas)     schematic dashboard
                      long-term history           (live SVG of the boat,
                                                  Atlas :8085 pattern)
                              ▲
   geometry: lines plan ──► hull surface (FreeCAD/OpenCASCADE) ──► STEP
   (digitize offsets)       AP216-shaped, viewable in the dashboard
```

Three principles:

1. **The point schema is the contract.** Sensors, dashboard, and history all
   conform to `schema/points.yaml`. Adding a sensor = one schema entry plus
   wiring, nothing else changes shape.
2. **Standards where they exist.** Signal K paths for live data, SFI codes
   for asset classification, STEP APs for geometry. Custom only where marine
   standards have no cell (leeboards).
3. **Nothing invented.** Engine models, tank counts, and electrical layout
   enter the twin from the vessel or its documents, not from memory or
   inference. Gaps are listed as gaps.

## Roadmap

- [ ] **Digitize the hull.** Trace stations from the Point Barnes lines plan
      into a table of offsets; loft the surface; export STEP. First test:
      displacement at the documented draft vs the class's published figures.
- [ ] **Confirm plant specifics aboard** (engine models, tank arrangement,
      battery banks) and fill the schema gaps.
- [ ] **Stand up Signal K** on the boat computer; map `points.yaml`.
- [ ] **History + dashboard**: VM remote-write over LTE; schematic SVG from
      the deck plan with live overlays.
- [ ] **Process models**: fuel polishing is done; add engine start/stop
      checklists and the leeboard deployment procedure as they stabilize.
