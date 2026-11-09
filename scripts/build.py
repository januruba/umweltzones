"""Build data exports and static GitHub Pages. Python standard library only."""
import hashlib
import html
import json
import re
import shutil
import unicodedata
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
DOCS = ROOT / 'docs'


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, separators=(',', ':')) + '\n')


def slug(value):
    value = value.replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue').replace('ß', 'ss')
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', value).strip('-')


def date(value):
    value = (value or '').strip()
    return datetime.strptime(value, '%d.%m.%Y').date().isoformat() if value else None


def positions(value):
    if isinstance(value, list) and len(value) >= 2 and isinstance(value[0], (int, float)):
        yield value
    else:
        for child in value:
            yield from positions(child)


def validate_feature(feature):
    if feature.get('type') != 'Feature' or not feature.get('id'):
        raise ValueError('Invalid Feature')
    p = feature['properties']
    if p['id'] != feature['id'] or p['status'] not in ('active', 'abolished', 'planned', 'unknown'):
        raise ValueError('Invalid identity or status')
    geometry = feature['geometry']
    if geometry['type'] not in ('Polygon', 'MultiPolygon'):
        raise ValueError('Expected Polygon or MultiPolygon')
    polygons = [geometry['coordinates']] if geometry['type'] == 'Polygon' else geometry['coordinates']
    if not polygons:
        raise ValueError('Empty geometry')
    for polygon in polygons:
        if not polygon:
            raise ValueError('Empty polygon')
        for ring in polygon:
            if len(ring) < 4 or ring[0] != ring[-1]:
                raise ValueError('Unclosed or short polygon ring')
    for point in positions(geometry['coordinates']):
        if len(point) != 2 or not -180 <= point[0] <= 180 or not -90 <= point[1] <= 90:
            raise ValueError('Invalid WGS84 coordinate')


def normalize(raw, source):
    registry = json.loads((ROOT / 'sources' / 'uba' / 'ids.json').read_text())
    features = []
    for feature in raw['features']:
        original = feature['properties']
        name = original['name'].strip()
        if name not in registry:
            raise ValueError(f'Add an explicit stable ID to sources/uba/ids.json: {name}')
        code = original['status']
        if code not in (3, -1):
            raise ValueError(f'Unknown UBA status: {code}; review before importing')
        coordinates = list(positions(feature['geometry']['coordinates']))
        xs, ys = [p[0] for p in coordinates], [p[1] for p in coordinates]
        props = {
            'id': registry[name], 'name': name, 'country': 'DE',
            'region': original.get('bundesland'), 'type': 'low_emission_zone',
            'status': 'active' if code == 3 else 'abolished',
            'status_basis': 'source_snapshot',
            'valid_from': date(original.get('stufe1')),
            'valid_to': date(original.get('aufhebung')),
            'retrieved_at': source['retrieved_at'], 'verified_at': None,
            'geometry_accuracy': 'schematic',
            'source': {'publisher': 'Umweltbundesamt', 'url': source['service_url'],
                       'object_id': original['OBJECTID'], 'license': source['license'],
                       'license_url': source['license_url'], 'attribution': source['attribution']},
            'source_attributes': {k: v for k, v in original.items() if not k.startswith('Shape')}
        }
        result = {'type': 'Feature', 'id': props['id'], 'bbox': [min(xs), min(ys), max(xs), max(ys)],
                  'properties': props, 'geometry': feature['geometry']}
        validate_feature(result)
        features.append(result)
    features.sort(key=lambda f: f['id'])
    if len({f['id'] for f in features}) != len(features):
        raise ValueError('Duplicate zone IDs')
    return features


def collection(features):
    return {'type': 'FeatureCollection', 'features': features}


def build():
    folder = ROOT / 'sources' / 'uba'
    source = json.loads((folder / 'source.json').read_text())
    raw_bytes = (folder / 'layer-7.geojson').read_bytes()
    if hashlib.sha256(raw_bytes).hexdigest() != source['sha256']:
        raise ValueError('Source checksum mismatch')
    raw = json.loads(raw_bytes)
    if len(raw['features']) != source['feature_count'] or raw.get('exceededTransferLimit'):
        raise ValueError('Incomplete source snapshot')
    features = normalize(raw, source)
    active = [f for f in features if f['properties']['status'] == 'active']
    abolished = [f for f in features if f['properties']['status'] == 'abolished']
    write_json(DATA / 'zones.geojson', collection(features))
    write_json(DATA / 'active.geojson', collection(active))
    write_json(DATA / 'abolished.geojson', collection(abolished))
    write_json(DATA / 'countries' / 'DE.geojson', collection(features))
    catalogue = [{**f['properties'], 'bbox': f['bbox'], 'geojson': f"zones/{f['id']}.geojson"} for f in features]
    write_json(DATA / 'zones.json', {'schema_version': '1.0', 'zones': catalogue})
    zones_folder = DATA / 'zones'
    if zones_folder.exists():
        shutil.rmtree(zones_folder)
    for f in features:
        write_json(zones_folder / (f['id'] + '.geojson'), collection([f]))
    manifest = {'schema_version': '1.0', 'version': '0.1.1', 'countries': ['DE'],
                'retrieved_at': source['retrieved_at'], 'records': len(features),
                'active_records': len(active), 'abolished_records': len(abolished),
                'count_unit': 'polygon_records_not_distinct_regulatory_zones',
                'source_status_independently_verified': False, 'source_sha256': source['sha256']}
    write_json(DATA / 'manifest.json', manifest)
    if (DOCS / 'data').exists():
        shutil.rmtree(DOCS / 'data')
    shutil.copytree(DATA, DOCS / 'data')
    (DOCS / 'assets').mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / 'src' / 'index.js', DOCS / 'assets' / 'zones.js')
    rows = '\n'.join(
        '<tr><td><a href="data/zones/' + html.escape(f['id']) + '.geojson">' + html.escape(f['properties']['name']) + '</a></td>'
        '<td>' + html.escape(f['properties']['region'] or '') + '</td>'
        '<td><span class="badge ' + f['properties']['status'] + '">' + ('Active in source' if f['properties']['status'] == 'active' else 'Abolished in source') + '</span></td>'
        '<td>' + (f['properties']['valid_to'] or '—') + '</td></tr>' for f in features)
    page = (ROOT / 'templates' / 'index.html').read_text()
    for key, val in {'ROWS': rows, 'COUNT': len(features), 'ACTIVE': len(active), 'ABOLISHED': len(abolished), 'DATE': source['retrieved_at'][:10]}.items():
        page = page.replace('{{' + key + '}}', str(val))
    (DOCS / 'index.html').write_text(page)
    (DOCS / '.nojekyll').write_text('')
    print(f'Built {len(features)} polygon records: {len(active)} active, {len(abolished)} abolished (source status).')


if __name__ == '__main__':
    build()
