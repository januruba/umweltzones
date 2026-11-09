# Low-emission zones · GeoJSON, Leaflet and Google Maps

Low-emission zone catalogue and GeoJSON boundaries, with examples for Leaflet and Google Maps and documentation ready for GitHub Pages. The initial dataset covers Germany using public data from the German Environment Agency (Umweltbundesamt, UBA).

## Live examples

- [GreenStickerGermany.com — low-emission zones in Germany](https://greenstickergermany.com/low-emission-zones/) — English.
- [EkoPlaketa.cz — map of German low-emission zones](https://www.ekoplaketa.cz/mapa-emisnich-zon/) — Czech.

## Included

- 60 polygon records: 37 active and 23 abolished **according to the source snapshot** retrieved on 9 November 2026.
- A JSON catalogue, combined GeoJSON, active and abolished subsets, country exports and individual files.
- English documentation, a searchable catalogue and runnable map examples.
- JavaScript helpers for Leaflet 1.9 and the Google Maps JavaScript API.
- Reproducible builds, data checks and a GitHub Pages workflow.

Polygon records are not the same as distinct regulatory zones. The source records Köln, Köln (Erweiterung 2019), Marburg (Zone Ost) and Marburg (Zone West) separately. Source names and geometries are preserved.

**This is a source snapshot, not an independently verified current list of entry rules.** See `data/manifest.json` for its retrieval date. UBA boundaries are schematic and do not include all exemptions. Additional diesel restrictions and individual road restrictions are not comprehensively covered.

## Run locally

Requires Python 3.10+ and Node.js 20+ for JavaScript tests. No npm or Python packages need to be installed.

```sh
npm run build
npm test
npm run serve
```

Open `http://localhost:8080`. Without npm, build with `python3 scripts/build.py` and serve with `python3 -m http.server 8080 --directory docs`. Open examples over HTTP because they use `fetch()` and ES modules.

## Repository layout

```text
data/                 Generated public exports
sources/uba/          Source snapshot, provenance, checksum and stable ID registry
src/index.js          Leaflet and Google Maps helpers
templates/index.html  Documentation source template
docs/                 Ready-to-publish GitHub Pages content, including data
scripts/              Source retrieval and static build
tests/                Data, geometry and adapter checks
.github/workflows/    Validation and GitHub Pages deployment
```

## Data exports

| Path | Contents |
| --- | --- |
| `data/zones.json` | Catalogue without coordinates, with individual GeoJSON links |
| `data/zones.geojson` | All polygon records |
| `data/active.geojson` | Records marked active by the source |
| `data/abolished.geojson` | Records marked abolished by the source |
| `data/countries/DE.geojson` | Germany, all statuses |
| `data/zones/<id>.geojson` | One polygon record as a FeatureCollection |
| `data/manifest.json` | Version, coverage, counts, retrieval time and source checksum |

On GitHub Pages, the same relative paths are available. These are static files rather than a server API. For production, keep your own copy or pin a specific repository commit or release; `main` may change.

## Leaflet

Load Leaflet 1.9.4 CSS and JavaScript, give the map container a height and create the map. Then:

```js
import { loadZones, addLeafletZones } from './src/index.js';

const data = await loadZones('./data/zones.geojson');
const layer = addLeafletZones(L, map, data, { country: 'DE' });
// Remove with map.removeLayer(layer).
```

Runnable example: `docs/examples/leaflet.html`. The example uses public OpenStreetMap tiles, which require attribution and compliance with the [tile usage policy](https://operations.osmfoundation.org/policies/tiles/). This repository provides zone boundaries; it does not distribute base map tiles.

## Google Maps

After loading the Maps JavaScript API and creating a map:

```js
import { loadZones, addGoogleZones } from './src/index.js';

const data = await loadZones('./data/zones.geojson');
const layer = addGoogleZones(google, map, data, { status: 'active' });
// Remove with layer.setMap(null).
```

Runnable example: `docs/examples/google.html`. It requires your own Maps JavaScript API key, an allowed HTTP referrer and enabled Google billing. The demo sends the key to Google to load the SDK and does not store it. Restrict your key to the required referrers and API. No API key is included in the repository. A live Google account integration has not been tested without a user-provided key.

### Shared helper options

| Option | Default | Purpose |
| --- | --- | --- |
| `status` | `active` | `active`, `abolished`, `planned`, `unknown` or `all` |
| `country` | No filter | Country code, such as `DE` |
| `fitBounds` | `true` | Fit the map to the selected geometries |
| `onEachFeature` | No callback | Leaflet only: additional per-feature layer configuration |

`selectZones(collection, options)` returns a filtered FeatureCollection. `zoneStyle(status)` returns basic styling. `loadZones(url, fetchOptions)` fetches and checks a response. GeoJSON coordinates remain `[longitude, latitude]`; both libraries handle this order natively.

## Data format

Each record is a GeoJSON Feature with `id`, `bbox`, `properties` and a Polygon or MultiPolygon geometry. Every boundary export is a FeatureCollection. Polygon components and interior holes are preserved.

Properties include `id`, `name`, `country`, `region`, `type`, `status`, `status_basis`, `valid_from`, `valid_to`, `retrieved_at`, `verified_at`, `geometry_accuracy`, `source` and `source_attributes`.

- `status_basis: source_snapshot`: status is taken from the source.
- `verified_at: null`: no independent verification has been recorded.
- `geometry_accuracy: schematic`: indicative boundaries as described by the source.
- `valid_from`: the first-stage date, `stufe1`, rather than necessarily the start of current entry requirements.
- `valid_to`: the effective abolition date reported by the source. Unknown dates are `null`.
- `source_attributes`: original attributes, including status codes and later-stage dates.

Source status `3` maps to `active`; `-1` maps to `abolished`. An unknown source status stops the build. The source layer name is not used to determine status because the layer includes both active and abolished records.

## Updates and contributions

See [CONTRIBUTING.md](CONTRIBUTING.md). Source refreshes are explicit and manual:

```sh
npm run update:uba
npm run build
npm test
git diff
```

Review source changes and licensing before publishing. Downloading data does not independently verify current rules. Do not edit generated `data/` or `docs/data/` files manually. Assign new names an explicit ID in `sources/uba/ids.json`. Keep the same ID when a name or status changes.

## GitHub Pages

Upload this directory's contents to a repository with a `main` branch, including `.github`. Set **Settings → Pages → Source → GitHub Actions**. On a push to `main`, the workflow builds and tests the project and publishes `docs/`. Pull requests only build and test. You can also start publication through **Actions → Validate and publish GitHub Pages → Run workflow**.

Internal links use relative paths and support GitHub Pages project URLs. The workflow does not schedule automatic source downloads.

## Sources and licensing

Code: [MIT](LICENSE). German source geodata: [GeoNutzV](https://sg.geodatenzentrum.de/web_public/gdz/lizenz/geonutzv.pdf), as stated in the [service metadata](https://md.umwelt.info/dataset/metadaten-uba/237cb80f-9129-435b-a3da-2df8fef0d0dc). See [DATA-LICENSE.md](DATA-LICENSE.md) for attribution and separate data terms.

- [UBA polygon layer](https://datahub.uba.de/server/rest/services/Lu/LU_UWZ_DFV_LRP/MapServer/7)
- [UBA zone overview](https://gis.uba.de/website/umweltzonen/)
- [Leaflet: GeoJSON](https://leafletjs.com/examples/geojson/)
- [Google Maps: Data layer](https://developers.google.com/maps/documentation/javascript/datalayer)
- [GitHub Pages: custom workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
