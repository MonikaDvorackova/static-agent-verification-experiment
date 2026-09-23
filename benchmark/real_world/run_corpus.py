"""Compare analyzers on three pinned, unmodified external source files.

Reads text and git metadata only; never imports or executes agent code.
"""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from benchmark.sdk_cases.adapter import analyze_tool
from src.analysis.engine import analyze

CASES = (
    ('openkb', 'VectifyAI/OpenKB', 'ff54396e575ee6feb0113b631a34caa082b441cc', 'openkb/agent/query.py'),
    ('copane', 'MostafaKashwaa/copane', 'e8392bb0730dee2f688acccff24fa0ba8f3ede29', 'python/src/copane/tools/write_file.py'),
    ('based_agent', 'Kkooops/OpenAI-Based-Agent', '9bbf71fc70dd266e1d67e5be697eea2e84b4cdf2', 'src/tools/write_file_tool.py'),
)


def run(checkouts: dict[str, Path]) -> dict:
    output = []
    for key, repo, expected, filename in CASES:
        checkout = checkouts[key]
        revision = subprocess.check_output(['git', '-C', str(checkout), 'rev-parse', 'HEAD'], text=True).strip()
        status = subprocess.check_output(['git', '-C', str(checkout), 'status', '--porcelain'], text=True).strip()
        if revision != expected or status:
            raise ValueError(f'{repo}: expected clean checkout at {expected}')
        source = (checkout / filename).read_text()
        output.append({
            'case': key, 'repository': repo, 'revision': revision, 'file': filename,
            'sha256': hashlib.sha256(source.encode()).hexdigest(),
            'original': {r.property: {'status': r.status, 'reason': r.reasons[0] if r.reasons else None}
                         for r in analyze(source, filename)},
            'sdk_adapter': {r.property: {'status': r.status, 'reason': r.reasons[0] if r.reasons else None}
                            for r in analyze_tool(source, filename)},
        })
    return {'cases': output}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('openkb', type=Path)
    parser.add_argument('copane', type=Path)
    parser.add_argument('based_agent', type=Path)
    args = parser.parse_args()
    print(json.dumps(run({k: getattr(args, k) for k, *_ in CASES}), indent=2))
