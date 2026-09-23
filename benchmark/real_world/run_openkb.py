"""Analyze a pinned external checkout without importing or executing its code."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from src.analysis.engine import analyze
from benchmark.sdk_cases.adapter import analyze_tool

REVISION = 'ff54396e575ee6feb0113b631a34caa082b441cc'
FILES = ('openkb/agent/query.py', 'openkb/agent/tools.py', 'openkb/locks.py')


def run(checkout: Path) -> dict:
    revision = subprocess.check_output(['git', '-C', str(checkout), 'rev-parse', 'HEAD'], text=True).strip()
    if revision != REVISION or subprocess.check_output(['git', '-C', str(checkout), 'status', '--porcelain'], text=True).strip():
        raise ValueError('checkout must be clean and pinned to ' + REVISION)
    files = []
    for relative in FILES:
        source = (checkout / relative).read_text()
        files.append({
            'path': relative, 'sha256': hashlib.sha256(source.encode()).hexdigest(),
            'original': {r.property: {'status': r.status, 'reasons': r.reasons[:3]}
                         for r in analyze(source, relative)},
            'sdk_adapter': {r.property: {'status': r.status, 'reasons': r.reasons[:3]}
                            for r in analyze_tool(source, relative)},
        })
    return {'repository': 'VectifyAI/OpenKB', 'revision': revision, 'files': files}


if __name__ == '__main__':
    cli = argparse.ArgumentParser()
    cli.add_argument('checkout', type=Path)
    args = cli.parse_args()
    print(json.dumps(run(args.checkout), indent=2))
