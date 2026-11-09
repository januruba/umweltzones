"""Explicit, manual refresh of the source snapshot; no scheduled publishing."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
SERVICE = 'https://datahub.uba.de/server/rest/services/Lu/LU_UWZ_DFV_LRP/MapServer/7'


def fetch():
    query = urlencode({'where': '1=1', 'outFields': '*', 'outSR': '4326', 'f': 'geojson'})
    url = SERVICE + '/query?' + query
    with urlopen(url, timeout=90) as response:
        raw = response.read()
    data = json.loads(raw)
    if data.get('type') != 'FeatureCollection' or not data.get('features'):
        raise ValueError('The source did not return a nonempty FeatureCollection')
    if data.get('exceededTransferLimit'):
        raise ValueError('The source is truncated; implement pagination before updating')
    with urlopen(SERVICE + '/query?' + urlencode({'where': '1=1', 'returnCountOnly': 'true', 'f': 'json'}), timeout=45) as response:
        count = json.load(response)['count']
    if len(data['features']) != count:
        raise ValueError('Feature count does not match source count')
    folder = ROOT / 'sources' / 'uba'
    manifest = json.loads((folder / 'source.json').read_text())
    manifest.update(retrieved_at=datetime.now(timezone.utc).isoformat(), query_url=url,
                    sha256=hashlib.sha256(raw).hexdigest(), feature_count=count)
    (folder / 'layer-7.geojson').write_bytes(raw)
    (folder / 'source.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(f'Downloaded {count} source records. Review the diff, then run npm run build and npm test.')


if __name__ == '__main__':
    fetch()
