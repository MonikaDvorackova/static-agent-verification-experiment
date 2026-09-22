import argparse
from pathlib import Path
from src.analysis.engine import analyze

parser = argparse.ArgumentParser(description='Experimental static agent analyzer')
parser.add_argument('source', type=Path)
args = parser.parse_args()
for result in analyze(args.source.read_text(), str(args.source)):
    print(result)
