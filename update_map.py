#!/usr/bin/env python3
"""Update travel-heatmap index.html with new trip data from receipts."""

import json
import re
import io
import sys
import random

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

INFILE = 'index.html'
OUTFILE = 'index.html'

with open(INFILE, 'r', encoding='utf-8') as f:
    content = f.read()

# ───── Extract nav ─────
nav_match = re.search(r'(    const nav = )(\[.*?\]);', content, re.DOTALL)
nav = json.loads(nav_match.group(2))

# ───── Extract arcTargets ─────
arc_match = re.search(r'(    const arcTargets = )(\[.*?\]);', content, re.DOTALL)
arc_targets = json.loads(arc_match.group(2))

# ───── Extract yearData (2026 only, to append points) ─────
yd_match = re.search(r'(    const yearData = )(\{.*?\});\s*\n', content, re.DOTALL)
year_data = json.loads(yd_match.group(2))

# ============================================================
# NEW DATA FROM RECEIPTS (Ireland 26, Turkey 26, Italy 26, Poland 26)
# ============================================================

new_points_2026 = []

def jitter(lat, lng, n=5, radius=0.02):
    """Create n slightly randomized points around (lat, lng)."""
    out = []
    random.seed(int(lat * 1000 + lng * 1000))
    for _ in range(n):
        out.append([
            lat + random.uniform(-radius, radius),
            lng + random.uniform(-radius, radius),
        ])
    return out

# ───── Ireland (NEW country) ─────
dublin = {'name': 'Dublin', 'lat': 53.3498, 'lng': -6.2603, 'visits': 8}
ireland_country = {
    'code': 'IE',
    'name': 'Ireland',
    'points': 8,
    'bounds': [[53.2, -6.5], [53.5, -6.0]],
    'cities': [dublin],
}
nav.append(ireland_country)
arc_targets.append({'name': 'Ireland', 'lat': dublin['lat'], 'lng': dublin['lng']})
new_points_2026 += jitter(dublin['lat'], dublin['lng'], n=8)

# ───── Poland (NEW country) ─────
warsaw = {'name': 'Warsaw', 'lat': 52.2297, 'lng': 21.0122, 'visits': 6}
poland_country = {
    'code': 'PL',
    'name': 'Poland',
    'points': 6,
    'bounds': [[52.0, 20.8], [52.4, 21.2]],
    'cities': [warsaw],
}
nav.append(poland_country)
arc_targets.append({'name': 'Poland', 'lat': warsaw['lat'], 'lng': warsaw['lng']})
new_points_2026 += jitter(warsaw['lat'], warsaw['lng'], n=6)

# ───── Switzerland (NEW country) ─────
lugano = {'name': 'Lugano', 'lat': 46.0037, 'lng': 8.9511, 'visits': 5}
ascona = {'name': 'Ascona', 'lat': 46.1534, 'lng': 8.7713, 'visits': 3}
switzerland_country = {
    'code': 'CH',
    'name': 'Switzerland',
    'points': 8,
    'bounds': [[45.9, 8.7], [46.2, 9.0]],
    'cities': [lugano, ascona],
}
nav.append(switzerland_country)
arc_targets.append({'name': 'Switzerland', 'lat': lugano['lat'], 'lng': lugano['lng']})
new_points_2026 += jitter(lugano['lat'], lugano['lng'], n=5)
new_points_2026 += jitter(ascona['lat'], ascona['lng'], n=3)

# ───── Italy: add Milano ─────
milano = {'name': 'Milano', 'lat': 45.4642, 'lng': 9.1900, 'visits': 10}
for c in nav:
    if c['code'] == 'IT':
        c['cities'].append(milano)
        c['points'] = c.get('points', 0) + 10
        # Expand bounds if needed
        b = c['bounds']
        b[0][0] = min(b[0][0], milano['lat'] - 0.05)
        b[0][1] = min(b[0][1], milano['lng'] - 0.05)
        b[1][0] = max(b[1][0], milano['lat'] + 0.05)
        b[1][1] = max(b[1][1], milano['lng'] + 0.05)
        break
new_points_2026 += jitter(milano['lat'], milano['lng'], n=10)

# ───── UK: add Coleraine (Northern Ireland) ─────
coleraine = {'name': 'Coleraine', 'lat': 55.1344, 'lng': -6.6640, 'visits': 4}
for c in nav:
    if c['code'] == 'GB':
        c['cities'].append(coleraine)
        c['points'] = c.get('points', 0) + 4
        b = c['bounds']
        b[0][0] = min(b[0][0], coleraine['lat'] - 0.05)
        b[0][1] = min(b[0][1], coleraine['lng'] - 0.05)
        b[1][0] = max(b[1][0], coleraine['lat'] + 0.05)
        b[1][1] = max(b[1][1], coleraine['lng'] + 0.05)
        break
new_points_2026 += jitter(coleraine['lat'], coleraine['lng'], n=4)

# ───── Turkey: add Istanbul (neighborhood coverage) ─────
istanbul = {'name': 'Istanbul', 'lat': 41.0082, 'lng': 28.9784, 'visits': 6}
for c in nav:
    if c['code'] == 'TR':
        c['cities'].append(istanbul)
        c['points'] = c.get('points', 0) + 6
        b = c['bounds']
        b[0][0] = min(b[0][0], istanbul['lat'] - 0.05)
        b[0][1] = min(b[0][1], istanbul['lng'] - 0.05)
        b[1][0] = max(b[1][0], istanbul['lat'] + 0.05)
        b[1][1] = max(b[1][1], istanbul['lng'] + 0.05)
        break
new_points_2026 += jitter(istanbul['lat'], istanbul['lng'], n=6)

# ───── USA Texas: add Houston ─────
houston = {'name': 'Houston', 'lat': 29.7604, 'lng': -95.3698, 'visits': 20}
for c in nav:
    if c['code'] == 'US':
        for s in c.get('states', []):
            if s['name'] == 'Texas':
                s['cities'].append(houston)
                sb = s['bounds']
                sb[0][0] = min(sb[0][0], houston['lat'] - 0.1)
                sb[0][1] = min(sb[0][1], houston['lng'] - 0.1)
                sb[1][0] = max(sb[1][0], houston['lat'] + 0.1)
                sb[1][1] = max(sb[1][1], houston['lng'] + 0.1)
                break
        c['points'] = c.get('points', 0) + 20
        break
new_points_2026 += jitter(houston['lat'], houston['lng'], n=20)

# ───── Append new GPS points to 2026 ─────
if '2026' not in year_data:
    year_data['2026'] = []
year_data['2026'] += new_points_2026

# ============================================================
# WRITE BACK
# ============================================================

new_nav_str = json.dumps(nav, ensure_ascii=False, separators=(',', ':'))
new_arcs_str = json.dumps(arc_targets, ensure_ascii=False, separators=(',', ':'))
new_yd_str = json.dumps(year_data, ensure_ascii=False, separators=(',', ':'))

content = re.sub(
    r'    const nav = \[.*?\];',
    '    const nav = ' + new_nav_str + ';',
    content,
    count=1,
    flags=re.DOTALL,
)
content = re.sub(
    r'    const arcTargets = \[.*?\];',
    '    const arcTargets = ' + new_arcs_str + ';',
    content,
    count=1,
    flags=re.DOTALL,
)
content = re.sub(
    r'    const yearData = \{.*?\};',
    '    const yearData = ' + new_yd_str + ';',
    content,
    count=1,
    flags=re.DOTALL,
)

with open(OUTFILE, 'w', encoding='utf-8') as f:
    f.write(content)

print('Updated travel heatmap:')
print('  + Ireland (Dublin)')
print('  + Poland (Warsaw)')
print('  + Switzerland (Lugano, Ascona)')
print('  + Italy: added Milano')
print('  + UK: added Coleraine')
print('  + Turkey: added Istanbul')
print('  + USA Texas: added Houston')
print(f'  + {len(new_points_2026)} new GPS points in 2026')
