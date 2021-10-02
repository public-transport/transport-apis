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

### Timezone Information

```js
{
    "timezone": "Europe/Berlin"
}
```

For endpoints that assume times in requests to be in a specific local timezone, the `timezone` field
should contain the [IANA timezone identifier](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) of the
expected timezone. This timezone can also be applied by clients to times in results returned by the endpoint,
particularly when the results are lacking explicit timezone (offset) information.

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
    "area": { /* GeoJSON polygon or MultiPolygon */ },
    "region": [ /* ISO-3166-1/2 codes */ ]
}
```

The following properties are defined for each coverage category:
* `area`: a GeoJSON Polygon or MultiPolygon defining the geographic area. This can be reasonably coarse; meter-precision is neither necessary nor practically meaningful.
* `region`: an array of ISO-3166-1 alpha 2 country codes, or ISO-3166-2 region codes covered.

Both fields should be provided.

### Attribution Information

The `attribution` property specifies licensing information for an endpoint.

#### Open Data

If an endpoint provides results under an Open Data license, `attribution`
generally follows the [Data Packages
format](https://dataprotocols.org/data-packages/):

```js
{
    "attribution": {
        "name": "© Helsinki Region Transport",
        "license": "CC-BY-4.0",
        "homepage": "https://www.hsl.fi/"
    }
}
```

Properties:
* `license`: An [Open Definition license ID](https://licenses.opendefinition.org/) or an [SPDX license id](https://spdx.org/licenses/).
* `name` and `homepage`: The entity to attribute for licenses requiring this.

name and license are mandatory, homepage is optional.

For endpoints aggregating data under various Open Data licenses, the situation can be
more complex than this though, making it impossible to specify a single license. This
can be expressed using the `mixedLicenses` property:

```js
{
    "attribution": {
        "name": "© navitia.io",
        "homepage": "https://www.navitia.io/",
        "mixedLicenses": true
    }
}
```

If `mixedLicenses` is set to `true`, the license details are provided in some
other form. This can be for example via the `homepage` property, or as part
of the endpoint responses themselves.

#### Proprietary

If an endpoint is known to be proprietary, `attribution` can be used to specify
this as well:

```js
{
    "attribution": {
        "isProprietary": true
    }
}
```

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
    "version": "1.27",
    "products": [
        {
            id: 'subway',
            name: 'U-Bahn'
            bitmasks: [1]
        },
        {
            id: 'suburban',
            bitmasks: [2],
            name: 'S-Bahn'
        },
        ...
    ]
}
```

The following properties are defined:
* `auth`: JSON object with static authentication information as passed verbatim in Hafas requests. Mandatory for all known endpoints.
* `checksumSalt`: A string containing a hexadecimal representation of the salt to hash the request body with. Mandatory for endpoints using this authentication mechanism.
* `client`: JSON object with static client information passed verbatim in Hafas requests.
* `ext`: String with the extension version (?) included in Hafas request.
* `micMacSalt`: A string containing a hexadecimal representation the salt to hash the hashed request body with. Mandatory for endpoints using this authentication mechanism.
* `version`: String containing the requested Hafas API version (?), mandatory for all known endpoints.
* `products`: Information about the Hafas product bitmask values and the corresponding product metadata (see below).

Product metadata consists of the following information:
* `id`: An URL-safe slug-ified version of the name, for machine use.
* `name`: A human-readable label for the product, as used by the operator.
* `bitmasks`: An array of integer values of bit values used by Hafas for this product.

#### Hafas query.exe

```js
"options": {
    "endpoint": "https://.../",
    "products": [
        {
            id: 'subway',
            name: 'U-Bahn'
            bitmasks: [1]
        },
        {
            id: 'suburban',
            bitmasks: [2],
            name: 'S-Bahn'
        },
        ...
    ]
}
```

The following properties are defined:
* `endpoint`: The base URL containing the various endpoints (`query.exe`, `stboard.exe`, etc).
* `products`: Hafas product metadata, see the Hafas mgate.exe variant above for the format details.

#### EFA

``` js
"options": {
    "endpoint": "https://...",
    "supportedOutputFormats": [ "XML", "JSON" ],
    "xmlOutputFormat": "full",
    "mId": "...",
    "stopfinderRequestCommand": "XSLT_STOPFINDER_REQUEST",
    "dmRequestCommand": "XSLT_DM_REQUEST",
    "tripRequestCommand": "XSLT_TRIP_REQUEST2"
}
```

The following properties are defined:
* `endpoint`: Base URL for EFA requests, mandatory.
* `supportedOutputFormats`: an array of strings containing valid arguments to the outputFormat parameter of an EFA query (`XML` and/or `JSON`).
* `xmlOutputFormat`: a string specifying the XML output format variant, either `full` or `compact`.
* `mId`: Value of the `mId` query argument. Omitted if not set.
* `stopfinderRequestCommand`: The command used for stop finder requests (default: `XML_STOPFINDER_REQUEST`).
* `dmRequestCommand`: The command used for departure monitor requests (defautl: `XML_DM_REQUEST`).
* `tripRequestCommand`: The command used for trip requests (default: `XML_TRIP_REQUEST2`).

#### Open Trip Planner with GraphQL

``` js
"options": {
    "endpoint": "https://...",
    "apiVersion": "otp2"
}
```

The following properties are defined:
* `endpoint`: Base URL for the API, without e.g. the `index/graphql` suffix.
* `apiVersion`: One of `otp1`, `otp2` or `entur`.

## Contributing

Note that, by participating in this project, you commit to the [code of conduct](code-of-conduct.md). If you want to contribute to this list, feel free to open an Issue at the [Issues page](https://github.com/public-transport/european-transport-operators/issues).
