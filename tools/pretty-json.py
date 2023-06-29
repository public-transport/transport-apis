#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2023 Volker Krause <vkrause@kde.org>
# SPDX-License-Identifier: MIT

# "Pretty" JSON formatting for the long coordinate arrays

import argparse
import json
import re

parser = argparse.ArgumentParser(description='Pretty JSON formatting for the Transport API data files.')
parser.add_argument('filename')
arguments = parser.parse_args()

# read as JSON and normalize to standard formatting
with open(arguments.filename, 'r') as f:
    j = json.loads(f.read())
s = json.dumps(j, indent=2)

# fold arrays of scalar values into one line
s = re.sub(r'\[\n +(\"[A-Za-z-]+\"|[\d.-]+)', r'[\1', s)
s = re.sub(r',\n +(\"[A-Za-z-]+\"|[\d.-]+)(?=[,\n])', r', \1', s)
s = re.sub(r'(?<![,\]}])\n +](\n|,\n)', r']\1', s)

# output
with open(arguments.filename, 'w') as f:
    f.write(s)
    f.write('\n')
