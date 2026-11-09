/** Filter a GeoJSON FeatureCollection. Active records are the default. */
export function selectZones(collection, { status = 'active', country } = {}) {
  if (collection?.type !== 'FeatureCollection' || !Array.isArray(collection.features)) {
    throw new TypeError('Expected a GeoJSON FeatureCollection');
  }
  return {
    type: 'FeatureCollection',
    features: collection.features.filter(({ properties: p, geometry }) =>
      geometry && (status === 'all' || p.status === status) && (!country || p.country === country))
  };
}

export async function loadZones(url, options = {}) {
  const response = await fetch(url, options);
  if (!response.ok) throw new Error(`GeoJSON request failed: ${response.status}`);
  const data = await response.json();
  if (data?.type !== 'FeatureCollection' || !Array.isArray(data.features)) {
    throw new TypeError('Expected a GeoJSON FeatureCollection');
  }
  return data;
}

export function zoneStyle(status) {
  const color = status === 'active' ? '#19754a' : status === 'abolished' ? '#707984' : '#be8223';
  return { color, weight: 2, fillColor: color, fillOpacity: 0.18 };
}

function popupContent(name, status) {
  const content = document.createElement('div');
  const title = document.createElement('strong');
  title.textContent = name;
  content.append(title, document.createElement('br'), document.createTextNode(status));
  return content;
}

/** L is the Leaflet 1.9 namespace. Returns an ordinary L.GeoJSON layer. */
export function addLeafletZones(L, map, collection, options = {}) {
  const layer = L.geoJSON(selectZones(collection, options), {
    style: feature => zoneStyle(feature.properties.status),
    onEachFeature(feature, child) {
      child.bindPopup(popupContent(feature.properties.name, feature.properties.status));
      options.onEachFeature?.(feature, child);
    }
  }).addTo(map);
  if (options.fitBounds !== false && layer.getBounds().isValid()) map.fitBounds(layer.getBounds(), { padding: [20, 20] });
  return layer;
}

/** google is the Maps JavaScript API namespace. Returns an independent Data layer. */
export function addGoogleZones(google, map, collection, options = {}) {
  const layer = new google.maps.Data({ map });
  const features = layer.addGeoJson(selectZones(collection, options), { idPropertyName: 'id' });
  layer.setStyle(feature => {
    const style = zoneStyle(feature.getProperty('status'));
    return { strokeColor: style.color, strokeWeight: style.weight, fillColor: style.fillColor, fillOpacity: style.fillOpacity };
  });
  const info = new google.maps.InfoWindow();
  layer.addListener('click', event => {
    info.setContent(popupContent(event.feature.getProperty('name'), event.feature.getProperty('status')));
    info.setPosition(event.latLng);
    info.open({ map });
  });
  if (options.fitBounds !== false && features.length) {
    const bounds = new google.maps.LatLngBounds();
    for (const feature of features) feature.getGeometry()?.forEachLatLng(point => bounds.extend(point));
    if (!bounds.isEmpty()) map.fitBounds(bounds);
  }
  return layer;
}
