# Project Log — NEM Carbon Intensity Analytics

This log tracks every meaningful decision made on this project, with
rationale. It's the raw material for the README's architecture section
and for explaining "why" in interviews.

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-07-27 | Use OpenNEM, not raw AEMO NEMWEB | Cleaner grain, analyst-friendly output, industry-standard starting point |
| 2026-07-27 | Scope to NSW1 + SA1, 30-min interval, 12 months | Coal-heavy vs renewables-heavy contrast makes comparisons meaningful; 30-min granularity is sufficient for the analytical questions, avoids unnecessary data volume |

## Open Questions
-

## Next Steps
-
## [2026-08-17] Data access method: API over manual CSV export

**Decision:** Use OpenElectricity API (scripted pull) instead of the site's manual CSV export button.

**Context:** OpenNEM has rebranded to OpenElectricity. The old open/keyless API is 
deprecated. The site's chart export offers fixed range presets (1D/3D/7D/30D/1Y/ALL) 
and a separate 5m/30m interval toggle. It was unclear whether 30m resolution is 
preserved reliably at 1Y range via the UI export, and this wasn't worth testing 
further.

**Rationale:**
- Project requires 30-min granularity across 12 months, 2 regions (NSW1, SA1) — 
  ~17.5k rows per region. Manual export doesn't scale or reproduce cleanly at that volume.
- A scripted API pull (via data_pipeline.py) is reproducible, auditable, and re-runnable 
  — which manual browser downloads are not. This is closer to how a real data pipeline 
  would be built.
- Requires registering a free API key at platform.openelectricity.org.au (new 
  requirement post-rebrand; the old anonymous access is gone).

**Trade-off accepted:** Slightly more setup time (API key registration, auth handling) 
in exchange for a defensible, professional pipeline design.

## [2026-08-21] API integration debugging: 5-min pull, region parsing

**Context:** First working end-to-end test pull from the OpenElectricity API 
(get_network_data), covering NSW1/SA1-adjacent groundwork before the full 
12-month build.

**Issues encountered and resolved, in order:**

1. **SSL certificate verification failure** — machine-level issue, not the API. 
   macOS Python.org install had a stale (2023) certificate bundle. Fixed via 
   `Install Certificates.command`.

2. **30-minute interval not supported by the live API** — despite matching 
   documented examples, the API only accepts 5m/1h/1d/7d/1M/3M/season/1y/fy. 
   Decision: pull at 5m resolution and aggregate to 30m in the pipeline, 
   preserving the original granularity requirement rather than dropping to 1h.

3. **Date parameter type mismatch** — the client library calls `.isoformat()` 
   internally, so it expects raw `datetime` objects, not pre-formatted strings.

4. **Unrelated library validation bug** on `get_facilities()` (a status value, 
   'commissioning', not recognised by the installed library version). Not 
   relevant to our actual data needs — `get_network_data()` is unaffected.

5. **Nested response structure** — `response.to_pandas()` silently dropped 
   region info. Root cause found by inspecting the raw response object directly: 
   structure is `response.data` (per metric) → `.results` (per region) → 
   `.data` (per timestamp) → `.root` (datetime, value). Solved by writing a 
   manual parsing loop instead of relying on the built-in conversion.

**Outcome:** Confirmed working pull of 5-min power data for all 5 NEM regions, 
correctly filterable to NSW1, with timezone-aware timestamps (+10:00 baked in).

**Principle reinforced:** when a library's behaviour doesn't match expectations, 
inspect the actual object/response directly (type, raw structure, pydantic's 
`model_fields`) rather than guessing at attribute names.