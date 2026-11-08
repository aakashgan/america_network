# Component 1 — Geographic Data & Dependency Network Engine

An offline-first, reusable Node MVP for the Richardson, Texas pilot. It turns fragmented **synthetic** organizational CSVs into a typed dependency graph while retaining source provenance and evidence level. It supports CBRE's data-unification challenge without claiming public map data verifies private utility or continuity relationships.

## Run

```sh
cd /Users/aakashganesh/component1-network-engine
npm test
npm run demo
npm start
curl -X POST http://localhost:3030/api/network/build -H 'content-type: application/json' -d '{"locationId":"richardson-tx"}'
curl 'http://localhost:3030/api/network/nodes/building%3ARCH-BLDG-012/dependencies?maxDepth=4'
```

No environment variables or package installation are required. Set `PORT` to change the API port. Build before using network read endpoints.

## Integration contract

Component 2 should consume `DependencyGraph` from `GET /api/network`, inspect coordinates/properties, then use `GET /api/network/nodes/:id/dependencies` for downstream propagation. Component 3 can use `/summary`, `/matches`, node lookup, edge evidence and explanations.

Edge direction is semantic and propagation-directed: `building → HOSTS → business → PROVIDES_SERVICE → service → SERVES_AREA → neighborhood`. `road → ACCESSIBLE_VIA → building` is intentionally not reversed. Traversal only follows outgoing edges.

## API

- `GET /api/health`, `GET /api/locations`
- `POST /api/network/build` accepts `{ locationId, options: { liveGeography } }`
- `GET /api/network`, `/api/network/summary`, `/api/network/matches`
- `GET /api/network/nodes/:id`
- `GET /api/network/nodes/:id/dependencies?maxDepth=4&relationshipTypes=HOSTS,PROVIDES_SERVICE`

The bundled geographic fixture is marked `synthetic_fixture`; live Overpass discovery is opt-in and has a timeout/fallback. The property, business, maintenance, resource records and service areas are synthetic. OSM, when available, supplies map features only—not verified equipment, utility, capacity, shelter, or business-continuity information.

## Design limits

CSV parsing is deliberately lightweight (no quoted-comma support), data is in memory, Richardson is the only configured location, and upload/multipart import is intentionally deferred. `src/types.js` exports stable node/edge enums, validation, location, and provenance helpers.

## Component 2 — Disaster simulation

Run the deterministic Richardson flood exercise with `npm run simulate`. The hypothetical polygon is in `data/simulations/richardson-flood.json`; community population, revenue, facility vulnerability, service demand, alternatives, and shelters are independently configured in `richardson-attributes.json` and are all explicitly synthetic. It consumes the Component 1 graph via the compatible offline provider—no external data is required.

Simulation API routes (after `npm start`):

- `GET /api/simulations/health`, `/api/simulations/scenarios`
- `POST /api/simulations/run` with `{"scenarioId":"richardson-flood-demo"}`
- `POST /api/simulations/compare` with `{"scenarioId":"richardson-flood-demo","modification":{"facilityStatus":{"building:RCH-BLDG-012":"operational"}}}`
- `GET /api/simulations/results/richardson-flood-demo`, `/impact`, `/timeline`
- `GET /api/simulations/results/richardson-flood-demo/nodes/building%3ARCH-BLDG-012`

The only fully implemented hazard is a flood. The model uses point-in-polygon exposure, transparent severity/vulnerability rules, relationship-specific propagation (`HOSTS`, `PROVIDES_SERVICE`, `SERVES_AREA`), illustrative revenue-at-risk, separate population displacement/shelter demand, and a four-step timeline. It is scenario analysis—not a forecast, damage model, official shelter directory, or verified business-continuity assessment.

## Component 3 — NVIDIA Nemotron investigation agent

The agent uses an allowlisted tool registry over the real Component 1 and Component 2 functions. It supports compact network inspection, node lookup, dependency tracing, simulation runs, impact reports, node explanations, and counterfactual comparisons. Tool execution IDs, arguments, status, duration, and summaries are retained per bounded in-memory session.

Copy `.env.example` to `.env` and set `NVIDIA_API_KEY` to use live NVIDIA. The default provider is `nvidia`; it fails clearly when a key is absent and does not claim live connectivity. The provider calls NVIDIA's OpenAI-compatible `chat/completions` endpoint using configured `NVIDIA_BASE_URL` and `NVIDIA_MODEL`. `AGENT_PROVIDER=mock_test` is only an explicitly labeled offline/test mode:

```sh
npm run agent:demo
```

Agent API: `GET /api/agent/health`, `GET /api/agent/tools`, `POST /api/agent/chat`, `GET /api/agent/sessions/:id`, `GET /api/agent/sessions/:id/trace`, and `POST /api/agent/sessions/:id/reset`.

## Feature 1 — real building footprints (Richardson pilot)

`src/buildings.js` is isolated from the dependency graph and simulator. It defines the small `richardson-tx` WGS84 rectangular study area (`[-96.731, 32.950, -96.727, 32.954]`), normalizes Overture `building` polygons/multipolygons, rejects malformed/duplicate/out-of-bound records, produces a representative footprint point, and writes versioned snapshots atomically. It does **not** create graph nodes or dependency relationships.

```sh
npm run data:buildings:fetch
npm run data:buildings:validate
npm run data:buildings:summary
curl 'http://localhost:3050/api/data/buildings?locationId=richardson-tx&limit=100'
curl 'http://localhost:3050/api/data/buildings?format=geojson&limit=100'
```

The fetch command uses the official Overture Maps client and caches only a complete GeoJSON response. It records the STAC-advertised release and acquisition time beside the raw extract, then validation creates `data/buildings/cache/richardson-tx-buildings.json` atomically. A failed refresh never replaces a valid snapshot. Overture's public buildings theme combines open sources and preserves original footprints; it should be attributed under its documented terms. If Overture or its S3 backend is unavailable and there is no valid cache, the endpoint fails explicitly rather than serving synthetic substitute footprints. The acquired raw file and snapshot are deliberately ignored from source control.

`GET /api/data/buildings?format=geojson&limit=100` returns provider-backed Polygon/MultiPolygon features. Optional `bbox=west,south,east,north`, `offset`, and `limit` constrain the response. The map renders these as a separate real-footprint layer; it does not infer graph dependencies from them.
