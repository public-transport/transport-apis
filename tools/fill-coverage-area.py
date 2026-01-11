#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2023 Volker Krause <vkrause@kde.org>
# SPDX-License-Identifier: MIT

# Fill missing coverage areas based on coverage region information
# using simplified ISO 3166-1/2 boundaries.

import argparse
import json
import math
import os
import pyclipper
import requests
import zipfile

parser = argparse.ArgumentParser(description='Fill in missing coverage area based on coverage regions')
parser.add_argument('filename')
parser.add_argument('--threshold', type=float, default=5000.0, help='Path simplification threshold (in meter)')
parser.add_argument('--region-threshold', action="append", nargs=2, help='[region] [meter] - Areas below this threshold in the given region will be dropped entirely')
parser.add_argument('--decimals', type=int, default=2, help='Number of decimals in coordinate output')
parser.add_argument('--bounding-box', type=float, nargs=4, help='Geographic bounding box filter (e.g. to exclude overseas territories) - minlat minlon maxlat maxlon')
# to exclude e.g.FR overseas territories: 36.5 -9 71 40
parser.add_argument('--force', default=False, help='Regenerate coverage area even if already present', action='store_true')
arguments = parser.parse_args()

#
# Locate/obtain ISO 3166-1/2 boundary GeoJSON data
#
ISO3166_1_VERSION = '2021-08-16'
ISO3166_1_URL = f"https://volkerkrause.eu/~vkrause/iso3166-boundaries/iso3166-1-boundaries.geojson-{ISO3166_1_VERSION}.zip"
ISO3166_2_VERSION = ISO3166_1_VERSION
ISO3166_2_URL = f"https://volkerkrause.eu/~vkrause/iso3166-boundaries/iso3166-2-boundaries.geojson-{ISO3166_2_VERSION}.zip"


def iso3166FilePath(name):
    return os.path.join(os.path.dirname(__file__), name)


def downloadIso3166File(url, name):
    fileName = iso3166FilePath(name)
    if os.path.exists(fileName):
        return
    print(f"Downloading {url}...")
    r = requests.get(url)
    if r.status_code < 400:
        with open(fileName, 'wb') as f:
            f.write(r.content)
        with zipfile.ZipFile(fileName, 'r') as z:
            z.extractall(os.path.dirname(__file__))

#
# Geometry/Geographic math
# Coordinates are assumed to be in GeoJSON format, ie. [lon, lat]


def lineLength(p1, p2):
    return pow(pow(p1[0] - p2[0], 2) + pow(p1[1] - p2[1], 2), 0.5)


# distance in meters between two geographic coordinates
def distance(p1, p2):
    earthRadius = 6371000.0
    d_lat = math.radians(p1[1] - p2[1])
    d_lon = math.radians(p1[0] - p2[0])
    a = pow(math.sin(d_lat / 2.0), 2) + math.cos(math.radians(p1[1])) * math.cos(math.radians(p2[1])) * pow(math.sin(d_lon / 2.0), 2)
    return 2.0 * earthRadius * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))


# distance in meters from p to a line given by coordinates l1 and l2
def distanceToLine(l1, l2, p):
    line_length = lineLength(l1, l2)
    if line_length == 0:
        return distance(l1, p)

    d = (p[0] - l1[0]) * (l2[0] - l1[0]) + (p[1] - l1[1]) * (l2[1] - l1[1])
    r = max(0.0, min(1.0, d / (line_length * line_length)))
    i = [l1[0] + r * (l2[0] - l1[0]), l1[1] + r * (l2[1] - l1[1])]
    return distance(i, p)


# min/max coordinates of a sequence of coordinates
def boundingBox(ring):
    minP = [180, 90]
    maxP = [-180, -90]
    for p in ring:
        minP = [min(minP[0], p[0]), min(minP[1], p[1])]
        maxP = [max(maxP[0], p[0]), max(maxP[1], p[1])]
    return [minP, maxP]


# Polygon simplification
def douglasPeucker(ring, threshold):
    if len(ring) < 3:
        return ring

    maxDistance = 0.0
    maxDistIdx = 1
    for i in range(1, len(ring) - 1):
        d = distanceToLine(ring[0], ring[-1], ring[i])
        if (d > maxDistance):
            maxDistance = d
            maxDistIdx = i

    if maxDistance > threshold:
        left = douglasPeucker(ring[:maxDistIdx], threshold)
        right = douglasPeucker(ring[maxDistIdx:], threshold)
        return left + right
    else:
        return [ring[0], ring[-1]]


# Finding and simplifying boundary polygons specificially for Transport API
def simplifyRing(regionCode, ring):
    bbox = boundingBox(ring)
    if arguments.bounding_box and (bbox[1][1] < arguments.bounding_box[0] or bbox[0][1] > arguments.bounding_box[2] or bbox[1][0] < arguments.bounding_box[1] or bbox[0][0] > arguments.bounding_box[3]):
        print(f"dropping polygon {bbox} outside of bounding box filter")
        return []

    # deal with tiny enclaves/exclaves like Baarle "in" BE/NL
    ringSize = distance(bbox[0], bbox[1])
    if ringSize < arguments.threshold:
        print("dropping polygon with bounding box below threshold")
        return []

    # apply per-region thresholds
    for rt in arguments.region_threshold:
        if regionCode == rt[0] and ringSize < float(rt[1]):
            print("dropping polygon with bounding box below region size threshold")
            return []

    ring_length = len(ring)
    ring = douglasPeucker(ring, arguments.threshold)
    if len(ring) < 5:
        print("polygon degenerated, using bounding box instead")
        ring = [bbox[0], [bbox[1][0], bbox[0][1]], bbox[1], [bbox[0][0], bbox[1][1]], bbox[0]]
    else:
        print(f"polygon simplification dropped {ring_length - len(ring)} of {ring_length} points")
    return ring

# Apply polygon offset (specified in meters) to the given ring
def offsetRing(ring, offset):
    # Clipper uses integer coordinates, so scale everything to the OSM-typcial 100 nano-degree
    CLIPPER_SCALE = 10000000

    bbox = boundingBox(ring)
    latCenter = (bbox[0][1] + bbox[1][1]) / 2.0
    bboxWidth = distance([bbox[0][0], latCenter], [bbox[1][0], latCenter])
    clipperOffset = ((bbox[1][0] - bbox[0][0]) / bboxWidth) * offset * CLIPPER_SCALE

    pc = pyclipper.PyclipperOffset()
    pc.AddPath(pyclipper.scale_to_clipper(ring, CLIPPER_SCALE), pyclipper.JT_MITER, pyclipper.ET_CLOSEDPOLYGON)
    result = pyclipper.scale_from_clipper(pc.Execute(clipperOffset), CLIPPER_SCALE)[0]
    if len(result) > 0:
        result.append(result[0]) # Clipper doesn't return closed polygons, but GeoJSON expects those
    return result

# Round coordinates in the given ring
def roundCoordinates(ring, decimals):
    for coordinate in ring:
        coordinate[0] = round(coordinate[0], decimals)
        coordinate[1] = round(coordinate[1], decimals)
    return ring

# Simplify a polygon, using the following approach:
# - Apply the Douglas-Peucker algorithm to remove points within arguments.threshold
# - Offset the outer ring by arguments.threshold to ensure we still cover the original polygon completely
# - Offset all inner rings by -arugments.threshold for the same reason
def simplifyMultiPolygon(regionCode, multiPoly):
    for i in range(0, len(multiPoly)):
        # outer ring
        multiPoly[i][0] = simplifyRing(regionCode, multiPoly[i][0])
        if not multiPoly[i][0]:
            multiPoly[i] = None
            continue
        multiPoly[i][0] = offsetRing(multiPoly[i][0], arguments.threshold)
        # inner rings
        for j in range(1, len(multiPoly[i])):
            multiPoly[i][j] = simplifyRing(regionCode, multiPoly[i][j])
            offsetRing(multiPoly[i][0], -arguments.threshold)
        multiPoly[i] = [roundCoordinates(ring, arguments.decimals) for ring in multiPoly[i] if ring]
    multiPoly = [poly for poly in multiPoly if poly]
    return multiPoly


def iso3166Boundary(regionCode, geojsonFile, featureKey):
    geojson = json.loads(open(geojsonFile, 'r').read())
    for region in geojson['features']:
        if region['properties'][featureKey] != regionCode:
            continue
        if region['geometry']['type'] == 'MultiPolygon':
            return simplifyMultiPolygon(regionCode, region['geometry']['coordinates'])
        else:
            return simplifyMultiPolygon(regionCode, [region['geometry']['coordinates']])


def iso3166_1Boundary(regionCode):
    downloadIso3166File(ISO3166_1_URL, f"iso3166-1-boundaries.geojson-{ISO3166_1_VERSION}.zip")
    return iso3166Boundary(regionCode, iso3166FilePath('iso3166-1-boundaries.geojson'), 'ISO3166-1')


def iso3166_2Boundary(regionCode):
    downloadIso3166File(ISO3166_2_URL, f"iso3166-2-boundaries.geojson-{ISO3166_2_VERSION}.zip")
    return iso3166Boundary(regionCode, iso3166FilePath('iso3166-2-boundaries.geojson'), 'ISO3166-2')


# Process Transport API files and fill in missing coverage area polygons
apiData = json.loads(open(arguments.filename, 'r').read())
for covAreaType in apiData['coverage']:
    coverage = apiData['coverage'][covAreaType]
    if 'area' in coverage and not arguments.force:
        continue

    multiPolygon = []
    for region in coverage['region']:
        if len(region) == 2:
            p = iso3166_1Boundary(region)
        else:
            p = iso3166_2Boundary(region)
        if p:
            multiPolygon += p

    # unite adjacent/overlapping polygons
    if len(multiPolygon) > 1:
        # Clipper uses integer coordinates, so scale everything to the OSM-typcial 100 nano-degree
        CLIPPER_SCALE = 10000000
        pc = pyclipper.Pyclipper()
        for poly in multiPolygon:
            pc.AddPaths(pyclipper.scale_to_clipper(poly, CLIPPER_SCALE), pyclipper.PT_SUBJECT, True)
        polyTree = pc.Execute2(pyclipper.CT_UNION, pyclipper.PFT_NONZERO, pyclipper.PFT_NONZERO)
        multiPolygon = []
        for node in polyTree.Childs:
            poly = pyclipper.scale_from_clipper(node.Contour, CLIPPER_SCALE)
            poly.append(poly[0]) # close polygons as expected by GeoJSON
            multiPolygon += [[poly]]
        for poly in multiPolygon:
            poly = [roundCoordinates(ring, arguments.decimals) for ring in poly if ring]


    if multiPolygon:
        area = {}
        if len(multiPolygon) == 1:
            area['type'] = 'Polygon'
            area['coordinates'] = multiPolygon[0]
        else:
            area['type'] = 'MultiPolygon'
            area['coordinates'] = multiPolygon
        coverage['area'] = area
        apiData['coverage'][covAreaType] = coverage

with open(arguments.filename, 'w') as f:
    f.write(json.dumps(apiData, indent=2))
