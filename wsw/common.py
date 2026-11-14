"""Shared I/O and interval conventions for WSW."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.1.0-pilot"
CATEGORIES = (
    "Science & Technology", "Finance", "Entertainment", "Current Affairs & News",
    "Sports", "Health & Fitness", "Education & Knowledge", "Lifestyle & Daily",
)


def read_rows(path):
    with Path(path).open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def write_rows(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n")


def write_json(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
                          encoding="utf-8")


def timestamp_ms(value):
    """Legacy labels have one-second resolution. Reject malformed clocks."""
    parts = value.strip().split(":")
    if len(parts) not in (3, 4) or any(not re.fullmatch(r"[0-9]{2}", part) for part in parts):
        raise ValueError(f"Invalid legacy timestamp: {value!r}")
    hours, minutes, seconds = map(int, parts[-3:])
    if (len(parts) == 4 and int(parts[0]) != 0) or minutes > 59 or seconds > 59:
        raise ValueError(f"Invalid legacy timestamp: {value!r}")
    return ((hours * 60 + minutes) * 60 + seconds) * 1000
