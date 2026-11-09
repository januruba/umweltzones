# Data licensing and provenance

## Germany — Umweltbundesamt

- Publisher: Umweltbundesamt (UBA), the German Environment Agency.
- Source: https://datahub.uba.de/server/rest/services/Lu/LU_UWZ_DFV_LRP/MapServer/7
- Original layer name: Umweltzonen – flächenhafte Darstellung.
- Service metadata: https://md.umwelt.info/dataset/metadaten-uba/237cb80f-9129-435b-a3da-2df8fef0d0dc
- Licence listed by the service metadata: GeoNutzVerordnung 20130319 (GeoNutzV).
- Licence text: https://sg.geodatenzentrum.de/web_public/gdz/lizenz/geonutzv.pdf
- Retrieval time, exact query URL and SHA-256: `sources/uba/source.json`.

Attribution used by this project:

**© Umweltbundesamt (UBA); modified: conversion to WGS84/GeoJSON and attribute normalization.**

Preserve source attribution and licensing information when redistributing the data. Display attribution and the modification notice in connection with the map. GeoNutzV permits commercial use subject to its terms. The project's MIT software licence does not relicense third-party geodata.

Geometries were requested directly from the service in WGS84 / GeoJSON. Boundaries are not manually moved, simplified or merged, and no new entry rules are inferred. Attributes are normalized, while original non-geometric attributes are retained in `source_attributes`.

UBA describes these boundaries as schematic and not covering all exemptions. The dataset does not replace local signage or complete official guidance. The source `status` attribute determines the status published here; individual records have not been independently verified for current accuracy.

## Mapping libraries and base maps

Leaflet is loaded from a CDN and retains its own licence. OpenStreetMap tiles are subject to OSM Foundation terms and tile usage policy. The Google Maps API and base maps are subject to Google's terms. Those terms are separate from the licensing of these zone boundaries.
