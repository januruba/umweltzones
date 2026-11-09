import copy
import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('builder', ROOT / 'scripts/build.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class DatasetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / 'data/zones.geojson').read_text())
        cls.source = json.loads((ROOT / 'sources/uba/source.json').read_text())
        cls.raw = json.loads((ROOT / 'sources/uba/layer-7.geojson').read_text())

    def test_snapshot_checksum_and_count(self):
        raw = (ROOT / 'sources/uba/layer-7.geojson').read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), self.source['sha256'])
        self.assertEqual(len(self.data['features']), self.source['feature_count'])

    def test_source_status_controls_exports_not_layer_name(self):
        for filename, status in [('active.geojson', 'active'), ('abolished.geojson', 'abolished')]:
            actual = json.loads((ROOT / 'data' / filename).read_text())['features']
            expected = [f for f in self.data['features'] if f['properties']['status'] == status]
            self.assertEqual(actual, expected)
            self.assertTrue(actual)
        for f in self.data['features']:
            self.assertEqual(f['properties']['status'], {3: 'active', -1: 'abolished'}[f['properties']['source_attributes']['status']])

    def test_normalization_preserves_all_geometry_coordinates(self):
        source_by_name = {f['properties']['name']: f['geometry'] for f in self.raw['features']}
        for f in self.data['features']:
            self.assertEqual(f['geometry'], source_by_name[f['properties']['name']])
            builder.validate_feature(f)

    def test_catalogue_and_individual_exports(self):
        catalogue = json.loads((ROOT / 'data/zones.json').read_text())['zones']
        self.assertEqual({x['id'] for x in catalogue}, {f['id'] for f in self.data['features']})
        for record in catalogue:
            individual = json.loads((ROOT / 'data' / record['geojson']).read_text())
            self.assertEqual([f['id'] for f in individual['features']], [record['id']])
            self.assertIsNone(record['verified_at'])

    def test_invalid_rings_and_coordinates_are_rejected(self):
        f = copy.deepcopy(self.data['features'][0])
        f['geometry'] = {'type': 'Polygon', 'coordinates': [[[0, 0], [1, 0], [1, 1], [0, 1]]]}
        with self.assertRaises(ValueError):
            builder.validate_feature(f)
        f['geometry']['coordinates'][0] = [[181, 0], [182, 0], [182, 1], [181, 0]]
        with self.assertRaises(ValueError):
            builder.validate_feature(f)

    def test_id_does_not_change_when_status_changes(self):
        raw = copy.deepcopy(self.raw)
        first = raw['features'][0]
        first['properties']['status'] = -1 if first['properties']['status'] == 3 else 3
        old = {f['properties']['name']: f['id'] for f in self.data['features']}
        self.assertEqual({f['properties']['name']: f['id'] for f in builder.normalize(raw, self.source)}, old)

    def test_unknown_source_status_fails_closed(self):
        raw = copy.deepcopy(self.raw)
        raw['features'][0]['properties']['status'] = 999
        with self.assertRaises(ValueError):
            builder.normalize(raw, self.source)

    def test_published_data_and_module_match_sources(self):
        for path in (ROOT / 'data').rglob('*'):
            if path.is_file():
                self.assertEqual(path.read_bytes(), (ROOT / 'docs/data' / path.relative_to(ROOT / 'data')).read_bytes())
        self.assertEqual((ROOT / 'src/index.js').read_bytes(), (ROOT / 'docs/assets/zones.js').read_bytes())


if __name__ == '__main__':
    unittest.main()
