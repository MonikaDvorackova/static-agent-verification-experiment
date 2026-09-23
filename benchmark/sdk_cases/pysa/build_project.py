"""Copy corpus with explicit type-only imports for Pysa; never execute it."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = Path(__file__).resolve().parent / 'project'
IMPORTS = ('from api import (llm, sensitive_data, validate, human_approve, '
           'human_approve_action, authorize_action, external_llm, external_tool, payment, db)\n')
for case in (ROOT / 'cases').glob('*.py'):
    source = case.read_text()
    assert source.startswith('from agents import Agent, function_tool\n')
    (TARGET / case.name).write_text(source.replace('from agents import Agent, function_tool\n',
                                                 'from agents import Agent, function_tool\n' + IMPORTS, 1))
