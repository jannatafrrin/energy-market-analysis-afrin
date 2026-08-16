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
