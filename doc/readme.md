# Transport API Metadata Format

## Overall Structure

There is a single JSON file per API endpoint.

## Endpoint Protocol

```json
{
    "type": {
        "hafasMgate": true
    }
}
```

Known protocols:
* `efa`
* `hafasMgate`
* `hafasQuery`
* `navitia`
* `otpGraphQl`
* `otpRest`

## Coverage Information

Describes the geographic area this endpoint provides results for.

```json
{
    "coverage": {
        "realtimeCoverage": { ... },
        "regularCoverage": { ... },
        "anyCoverage": { ... }
    }
}
```

There's three coverage categories:
* `realtimeCoverage`: In this area the endpoint provides accurate and highly detailed information.
  This is typically the are the operator can rely on live data about their own vehicles.

* `regularCoverage`: In this area reasonably complete data is available, but e.g. realtime data from other operators is missing or inaccurate quite often.

* `anyCoverage`: In this are only incomplete and/or shallow data is available. This is commonly the case in areas outside of the operating area,
e.g. long-distance trains & buses but not local modes of transport, or planned data but not realtime data.
You could say that this is the extent to which, in a region, the API provides any data.

At least one of those three entries must be provided.

```json
{
    "area": { GeoJSON polygon },
    "region": [ ISO-3166-1/2 codes ]
}
```

Per coverage are the following properties are defined:
* `area`: a GeoJSON polygon defining the geographic area. This can be reasonably coarse, meter-precision for example is neither necessary not practically meaningful.
* `region`: an array of ISO-3166-1 alpha 2 country codes, or ISO-3166-2 region codes covered.

Both fields should be provided.
