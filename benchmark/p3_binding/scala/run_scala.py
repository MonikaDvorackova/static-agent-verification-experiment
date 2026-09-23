"""Compile independent Scala 3 capability probes (requires Scala CLI 1.17.1)."""
from __future__ import annotations

import os
from pathlib import Path
import subprocess


CASES = {
    'Allowed.scala': (0, ''),
    'Denied.scala': (1, 'No given instance of type Pay'),
    'CaptureDenied.scala': (1, 'capability `pay` cannot flow into capture set {}'),
    'CastDenied.scala': (1, 'Cannot use asInstanceOf in safe mode'),
}


def main() -> None:
    directory = Path(__file__).parent
    cli = os.environ.get('SCALA_CLI', 'scala-cli')
    for filename, (expected_exit, expected_message) in CASES.items():
        command = [cli, 'compile', str(directory / filename),
                   '--server=false', '--scala', '3.9.0', '--jvm', 'system']
        if repository := os.environ.get('SCALA_REPOSITORY_URL'):
            command.extend(('--repository', repository))
        result = subprocess.run(command, capture_output=True, text=True,
                                check=False, timeout=180)
        output = result.stdout + result.stderr
        if (result.returncode == 0) != (expected_exit == 0) or expected_message not in output:
            raise AssertionError(f'{filename}: unexpected compiler result:\n{output[-2000:]}')
        print(f'{filename}: {"accepted" if expected_exit == 0 else "rejected"}')


if __name__ == '__main__':
    main()
