"""Evaluate the unchanged prototype on the labeled SDK-shaped corpus; source is never run."""
import csv
import json
from pathlib import Path
from src.analysis.engine import analyze
from benchmark.sdk_cases.adapter import analyze_tool

ROOT = Path(__file__).parent
PROPERTIES = ('P1', 'P2', 'P3')


def evaluate() -> dict:
    with (ROOT / 'labels.tsv').open() as label_file:
        rows = list(csv.DictReader(label_file, delimiter='\t'))
    observations = []
    for row in rows:
        filename = ROOT / 'cases' / (row['case'] + '.py')
        results = analyze(filename.read_text(), str(filename))
        adapted = analyze_tool(filename.read_text(), str(filename))
        observations.append({
            'case': row['case'], 'labels': {p: row[p] for p in PROPERTIES},
            'observed': {r.property: r.status for r in results},
            'adapted': {r.property: r.status for r in adapted},
            'reasons': {r.property: list(r.reasons) for r in results},
            'adapted_reasons': {r.property: list(r.reasons) for r in adapted},
        })
    cells = [(entry['labels'][p], entry['observed'][p]) for entry in observations for p in PROPERTIES]
    adapted_cells = [(entry['labels'][p], entry['adapted'][p]) for entry in observations for p in PROPERTIES]
    summary = {
        'cases': len(observations), 'property_decisions': len(cells),
        'labeled': {s: sum(expected == s for expected, _ in cells) for s in ('PROVED', 'VIOLATED', 'UNKNOWN')},
        'observed': {s: sum(actual == s for _, actual in cells) for s in ('PROVED', 'VIOLATED', 'UNKNOWN')},
        'false_proved_against_labels': sum(actual == 'PROVED' and expected != 'PROVED' for expected, actual in cells),
        'adapted_observed': {s: sum(actual == s for _, actual in adapted_cells) for s in ('PROVED', 'VIOLATED', 'UNKNOWN')},
        'adapted_false_proved_against_labels': sum(actual == 'PROVED' and expected != 'PROVED' for expected, actual in adapted_cells),
        'adapted_mismatches': sum(expected != actual for expected, actual in adapted_cells),
    }
    return {'summary': summary, 'cases': observations}


if __name__ == '__main__':
    print(json.dumps(evaluate(), indent=2))
