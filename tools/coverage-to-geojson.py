#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2021 Volker Krause <vkrause@kde.org>
# SPDX-License-Identifier: MIT
#
# Generates a GeoJSON document from coverage areas of Transport API data
#

import argparse
import glob
import json
import os
import re

parser = argparse.ArgumentParser(description='Generates a GeoJSON document from coverage areas of the Transport API Repository')
parser.add_argument('--data', type=str, required=True, help='Path to the Transport API data')
arguments = parser.parse_args()

output = {}
output['type'] = 'FeatureCollection'
output['name'] = 'Transport API Repository Coverage Data'
output['features'] = []

transportApiFiles = glob.glob(arguments.data + "/*/*.json", recursive=True)
for transportApiFile in transportApiFiles:
    f = open(transportApiFile, 'r')
    j = json.load(f)
    nameMatch = re.search('/([a-z]{2})/(.*)\\.json', transportApiFile)
    if nameMatch:
        name = nameMatch.group(1) + '-' + nameMatch.group(2)
    else:
        name = os.path.splitext(os.path.basename(transportApiFile))[0]

    for cov in ['anyCoverage', 'regularCoverage', 'realtimeCoverage']:
        if not 'coverage' in j or not cov in j['coverage'] or not 'area' in j['coverage'][cov]:
            continue
        properties = {}
        properties['name'] = name + '-' + cov
        feature = {}
        feature['type'] = 'Feature'
        feature['properties'] = properties
        feature['geometry'] = j['coverage'][cov]['area']
        output['features'].append(feature)

print(json.dumps(output))
