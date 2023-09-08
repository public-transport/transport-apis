#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2023 Volker Krause <vkrause@kde.org>
# SPDX-License-Identifier: MIT

import argparse
import glob
import os
import re

parser = argparse.ArgumentParser(
    description='Fill in missing coverage area based on coverage regions for all files')
parser.add_argument('--data', type=str, required=True, help='Path to the Transport API data')
arguments = parser.parse_args()

# bounding box filter for overseas territories
bounding_areas = {};
for country in ['at', 'be', 'ch', 'de', 'dk', 'ee', 'fi', 'ie', 'it', 'lu', 'nl', 'no', 'pl', 'se']:
    bounding_areas[country] = ['36.5', '-9', '71', '40']

transportApiFiles = glob.glob(arguments.data + "/*/*.json", recursive=True)
for transportApiFile in transportApiFiles:
    nameMatch = re.search('/([a-z]{2})/(.*)\\.json', transportApiFile)
    if not nameMatch:
        continue
    country = nameMatch.group(1)
    print (f"Processing {transportApiFile}")

    args = ['--threshold', '5000', '--decimals', '2']
    if country in bounding_areas:
        args += ['--bounding-box']
        args += bounding_areas[country]
    args += [transportApiFile]
    os.system(os.path.join(os.path.dirname(__file__), 'fill-coverage-area.py') + ' ' + ' '.join(args))
    os.system(os.path.join(os.path.dirname(__file__), 'pretty-json.py') + ' ' + transportApiFile)

os.system(os.path.join(os.path.dirname(__file__), 'coverage-to-geojson.py') + ' --data ' + arguments.data + ' > coverage.geojson')
