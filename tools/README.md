# Maintenance and QA tools

What's in here:
* `pretty-json.py`: JSON formater that folds scalar value arrays into a single line.
  This helps with keeping files at a manageable and readable size despite containing
  high-resolution GeoJSON coverage areas.
* `coverage-to-geojson.py`: Collect coverage areas from all API endpoint files and
  generate a single GeoJSON file from those. That can for example be imported into
  QGIS for reviewing geographical coverage areas in relation to a map and/or in relation
  to each other.
* `fill-coverage-area.py`: Adds missing coverage area polygons based on specified ISO 3166-1/2
  coverage region codes. This includes reducing high-resolution data to a level of detail
  appropriate for the use here.

Running `build.py` will run all of the above.

The necessary dependencies can be installed using `pip install -r requirements.txt`.

## Updating Transitous coverage areas

```
./tools/fill-coverage-area.py --force data/un/transitous.json \
  --decimals 2 --threshold 5000 \
  --region-threshold US 150000 \
  --region-threshold AU 150000 \
  --region-threshold NZ 150000 \
  --region-threshold UM 150000 \
  --region-threshold BR 150000 \
  --region-threshold CL 150000 \
  --region-threshold IN 150000 \
  --region-threshold JP 150000
./tools/pretty-json.py data/un/transitous.json
```
