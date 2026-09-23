"""Summarize Pysa alerts; absence of an alert is not a proof."""
import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
with (ROOT / 'labels.tsv').open() as label_file:
    labels = {r['case']: r for r in csv.DictReader(label_file, delimiter='\t')}
issues = json.loads((Path(__file__).parent / 'results.json').read_text())
properties = {6101: 'P1', 6102: 'P2', 6103: 'P3'}
hits = {(Path(issue['path']).stem, properties[issue['code']]) for issue in issues
        if issue['code'] in properties and Path(issue['path']).stem in labels}
print('issues:', len(issues), 'deduplicated property alerts:', len(hits))
for property_name in ('P1', 'P2', 'P3'):
    expected = {case for case, row in labels.items() if row[property_name] == 'VIOLATED'}
    detected = {case for case, prop in hits if prop == property_name}
    print(property_name, 'known violations detected:', len(expected & detected), '/', len(expected),
          'missed:', ', '.join(sorted(expected - detected)) or 'none',
          'alerts on UNKNOWN labels:', len({case for case in detected if labels[case][property_name] == 'UNKNOWN'}))
