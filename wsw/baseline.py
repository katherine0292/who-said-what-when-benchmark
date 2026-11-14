"""Generate blind diagnostic baselines using only model-facing input metadata."""
import argparse
from pathlib import Path

from .common import ROOT, read_rows, write_rows


def predict(inputs, mode):
    for row in inputs:
        length = row["duration_ms"]
        evidence = [0, length] if mode == "whole" else [length * 2 // 5, (length * 3 + 4) // 5]
        yield {"id": row["id"], "speaker_id": "spk_01", "evidence_ms": [evidence]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", type=Path, default=ROOT / "data/inputs.jsonl")
    parser.add_argument("--mode", choices=("whole", "middle"), default="whole")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    write_rows(args.out, predict(read_rows(args.inputs), args.mode))


if __name__ == "__main__":
    main()
