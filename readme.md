# list of transport APIs

**This is a machine-readable list of (public) transport API endpoints**, with details about who operates them, the protocol used & authentication details.


## Format

### Overall Structure

There is a single JSON file per API endpoint. It must contain the following
properties:

* `name`: endpoint name
* `type`: endpoint protocol description (see below)
* `supportedLanguages`: list of supported languages (see below)
* `coverage`: the geographic area this endpoint provides results for (see below)
* `options`: protocol-specific options (not specified here)

### Endpoint Protocol

```js
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

### Supported Languages

```js
{
    "supportedLanguages": [
        "en",
        "de",
        "fr",
        "es"
    ]
}
```

A list of ISO-639-1 language codes describing the languages supported by the
endpoint.

### Coverage Information

Describes the geographic area this endpoint provides results for.

```js
{
    "coverage": {
        "realtimeCoverage": { /* ... */ },
        "regularCoverage": { /* ... */ },
        "anyCoverage": { /* ... */ }
    }
}
```

There's three coverage categories:
* `realtimeCoverage`: In this area the endpoint provides accurate and highly detailed information.
  This is typically where the operator can rely on live data about their own vehicles.

* `regularCoverage`: In this area reasonably complete data is available, but e.g. realtime data from other operators is missing or inaccurate quite often.

* `anyCoverage`: In this area only incomplete and/or shallow data is available. This is commonly the case in areas outside of the operating area,
e.g. long-distance trains & buses but not local modes of transport, or planned data but not realtime data.
You could say that this is the extent to which, in a region, the API provides any data.

At least one coverage category must be provided.

```js
{
    "area": { /* GeoJSON polygon */ },
    "region": [ /* ISO-3166-1/2 codes */ ]
}
```

The following properties are defined for each coverage category:
* `area`: a GeoJSON polygon defining the geographic area. This can be reasonably coarse, meter-precision for example is neither necessary nor practically meaningful.
* `region`: an array of ISO-3166-1 alpha 2 country codes, or ISO-3166-2 region codes covered.

Both fields should be provided.

### Protocol Specific Options

#### Hafas mgate.exe

```js
"options": {
    "auth": {
        "aid": "...",
        ...
    },
    "checksumSalt": "<hex value>",
    "client": {
        "id": "...",
        "type": "...",
        ...
    },
    "ext": "...",
    "micMacSalt": "<hex value>",
    "version": "1.27"
}
```

The following properties are defined:
* `auth`: JSON object with static authentication information as passed verbatim in Hafas requests. Mandatory for all known endpoints.
* `checksumSalt`: A string containing a hexadecimal representation of the salt to hash the request body with. Mandatory for endpoints using this authentication mechanism.
* `client`: JSON object with static client information passed verbatim in Hafas requests.
* `ext`: String with the extension version (?) included in Hafas request.
* `micMacSalt`: A string containing a hexadecimal representation the salt to hash the hashed request body with. Mandatory for endpoints using this authentication mechanism.
* `version`: String containing the requested Hafas API version (?), mandatory for all known endpoints.

## Contributing

Note that, by participating in this project, you commit to the [code of conduct](code-of-conduct.md). If you want to contribute to this list, feel free to open an Issue at the [Issues page](https://github.com/public-transport/european-transport-operators/issues).
