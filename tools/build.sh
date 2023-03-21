#!/bin/sh
# SPDX-FileCopyrightText: 2023 Volker Krause <vkrause@kde.org>
# SPDX-License-Identifier: MIT

scriptdir=`dirname "${BASH_SOURCE[0]:-$0}"`
datadir=$scriptdir/../data



for j in `find $datadir -name "*.json"`; do
    country=`echo "$j" | sed -e 's,^.*/\([a-z][a-z]\)/.*$,\1,'`
    echo "Processing $country/`basename $j`"

    # bounding box filter for overseas territories
    bbox=""
    for c in at be ch de dk ee fi ie it lu nl no pl se; do
        if [ "$country" == "$c" ]; then
            bbox="--bounding-box 36.5 -9 71 40"
            break
        fi
    done

    $scriptdir/fill-coverage-area.py --threshold 5000 --decimals 2 $bbox $j
    $scriptdir/pretty-json.py $j
done

$scriptdir/coverage-to-geojson.py --data "$datadir" > coverage.geojson
