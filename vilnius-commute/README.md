# Vilnius rental search – kindergarten + school morning commute

Fixed points (geocoded with Nominatim / OSM):
- Kindergarten: Markučių l/d, Pakraščio g. 15 — 54.6754507, 25.3193472
- School: Filaretų pradinė mokykla, Filaretų g. 43A — 54.6850765, 25.3131255

Day modelled: Wednesday 2026-11-18, school arrival ≤ 08:00, walking + Vilnius public transport.
Data: stops.lt GTFS (2026-11-15), OSM Lithuania extract from geo2day.com (Geofabrik unreachable from the build environment).
Router: r5py 1.1.7, per-minute departures, 200 m grid within 7 km.

Results (leg 2 measured from when the mother leaves the kindergarten):
- Kindergarten first: 193 qualifying cells (both legs ≤ 20 min), 162 borderline (≤ 25 min).
- School first: 0 qualifying cells, 383 borderline.
- The critical K→S leg is 20 min by r5py/GTFS (leave 07:31) but 22 min by the stops.lt planner for the same buses; an earlier K→S trip (leave 07:08 → school 07:28) is 20 min in both.

Files:
- `commute_zone_map.html` — zone + listings map
- `zone_KS_qualifying.geojson`, `zone_KS_borderline.geojson`, `zone_SK_borderline.geojson` — zone polygons
- `zone_cells.geojson` — per-cell classes and times (both orders)
- `listings_with_commutes.json` — all 95 listings checked with chained commute results
- `scripts/` — routing, chaining, scraping-parse and map scripts
