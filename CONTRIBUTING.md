# Contributing and updating data

1. Use a traceable source and record its licence, URL and retrieval time. Keep independent verification separate from downloading a snapshot.
2. For UBA, run `npm run update:uba`. The script checks downloaded records against the count reported by the service, rejects truncated responses and stores a checksum. Publishing still requires a subsequent push.
3. Compare the new snapshot with the previous version. Review changes to statuses, dates, boundaries and licensing.
4. Assign new names an explicit ID in `sources/uba/ids.json`. When a name changes, move its mapping to the new name while keeping the same ID. Two names must not receive the same ID. Merge shared or multipart zones only when their regulatory meaning is documented.
5. Run `npm run build` and `npm test`. Checks cover unique IDs, supported statuses, WGS84 coordinate ranges, closed polygon rings, catalogue/export consistency and preservation of multipart geometry. These checks do not establish complete topological validity; inspect substantial boundary changes in a GIS as well.
6. Inspect the map using `npm run serve`. When changing the Google integration, also test a real map with your own test API key.
7. Commit the snapshot, source manifest, any ID registry changes and all generated exports. Describe the actual changes and supporting sources in the pull request.

Adding a country requires a source adapter and a review of its licence. The current build covers the documented German dataset. Do not contribute guessed boundaries or inferred vehicle entry requirements.
