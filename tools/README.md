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

Running `build.sh` will run all of the above.
