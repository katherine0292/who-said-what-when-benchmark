"""Verify referential integrity, timing bounds, pilot summary, and split isolation."""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import re
import sys

from .common import CATEGORIES, ROOT, VERSION, read_rows
from .score import index, valid_windows


def check(condition, message):
    if not condition:
        raise ValueError(message)


def validate(data):
    inputs = index(read_rows(data / "inputs.jsonl"))
    refs = index(read_rows(data / "references.jsonl"))
    audits = index(read_rows(data / "migration_audit.jsonl"))
    rows = read_rows(data / "clips.jsonl")
    clips = {row["clip_id"]: row for row in rows}
    check(len(clips) == len(rows) > 0, "Duplicate or empty clip manifest")
    check(set(inputs) == set(refs) == set(audits) and bool(inputs), "QA ID coverage mismatch")
    turns, sources = defaultdict(dict), defaultdict(set)
    for turn in read_rows(data / "turns.jsonl"):
        clip_id, turn_id = turn["clip_id"], turn["turn_id"]
        check(clip_id in clips and type(turn_id) is int and turn_id > 0 and turn_id not in turns[clip_id],
              f"{clip_id}: invalid turn ID {turn_id}")
        clip = clips[clip_id]
        status = turn["clock_status"]
        a, b = turn["start_ms"], turn["end_ms"]
        check(type(a) is int and a >= 0 and (b is None or type(b) is int), f"{clip_id}: invalid clock data type")
        expected = ("invalid_legacy_clock" if b is None or a >= b else
                    "exceeds_audio" if b > clip["duration_ms"] + 1000 else "legacy")
        check(status == expected and (status == "legacy" or clip["status"] == "needs_media_review"),
              f"{clip_id}: clock and review status conflict")
        check(bool(re.fullmatch(r"spk_[0-9]{2,}", turn["speaker_id"])), f"{clip_id}: invalid speaker ID")
        turns[clip_id][turn_id] = turn
    windows = Counter((row["source_id"], *row["source_window_reported_ms"]) for row in rows)
    for clip_id, clip in clips.items():
        duration = clip["duration_ms"]
        origin_start, origin_end = clip["source_window_reported_ms"]
        flags = clip["review_flags"]
        check(type(duration) is int and duration > 0 and 0 <= origin_start < origin_end, f"{clip_id}: invalid duration")
        check(clip["category"] in CATEGORIES and clip["split"] == "pilot", f"{clip_id}: invalid category or split")
        check(clip["status"] == ("needs_media_review" if flags else "text_aligned"), f"{clip_id}: invalid status")
        check((abs(origin_end - origin_start - duration) > 1500) == ("origin_duration_mismatch" in flags),
              f"{clip_id}: duration mismatch flag")
        check((windows[(clip["source_id"], origin_start, origin_end)] > 1) == ("duplicate_source_window" in flags),
              f"{clip_id}: duplicate source window flag")
        check(len(turns[clip_id]) == clip["turn_count"]
              and len({t["speaker_id"] for t in turns[clip_id].values()}) == clip["speaker_count"],
              f"{clip_id}: invalid turn or speaker count")
        sources[clip["source_id"]].add(clip["split"])
    check(all(len(splits) == 1 for splits in sources.values()), "Source video appears across splits")
    covered = set()
    for qid, inp in inputs.items():
        ref, audit, clip_id = refs[qid], audits[qid], inp["clip_id"]
        check(bool(re.fullmatch(r"wsw_[0-9]{4,}", qid)), f"{qid}: invalid QA ID")
        check(set(inp) == {"id", "clip_id", "duration_ms", "language", "question"},
              f"{qid}: unexpected field in model input")
        check(clip_id in clips and ref["clip_id"] == audit["clip_id"] == clip_id, f"{qid}: invalid clip link")
        clip = clips[clip_id]
        covered.add(clip_id)
        check(inp["duration_ms"] == clip["duration_ms"] and inp["language"] == clip["language"],
              f"{qid}: clip and input metadata differ")
        check(ref["status"] == clip["status"] and ref["split"] == clip["split"]
              and audit["flags"] == clip["review_flags"], f"{qid}: review/split mismatch")
        check(isinstance(inp["question"], str) and inp["question"].strip()
              and ref["key_points"] and all(isinstance(x, str) and x.strip() for x in ref["key_points"]),
              f"{qid}: empty question or answer points")
        check(ref["turn_ids"] == sorted(set(ref["turn_ids"])) and ref["turn_ids"] == audit["canonical_turn_ids"]
              and ref["turn_ids"], f"{qid}: invalid reference turn IDs")
        evidence = ref["evidence_ms"]
        check(valid_windows(evidence, inp["duration_ms"]), f"{qid}: out of bounds evidence")
        linked = []
        for turn_id in ref["turn_ids"]:
            turn = turns[clip_id].get(turn_id)
            check(turn and turn["speaker_id"] == ref["speaker_id"] and turn["clock_status"] == "legacy",
                  f"{qid}: invalid evidence turn")
            a, b = turn["start_ms"], turn["end_ms"]
            if linked and a <= linked[-1][1]:
                linked[-1][1] = max(linked[-1][1], b)
            else:
                linked.append([a, b])
        check(linked == evidence, f"{qid}: evidence windows do not match reference turns")
    check(covered == set(clips), "Clip without a question")
    summary = json.loads((data / "summary.json").read_text(encoding="utf-8"))
    expected = {"version": VERSION, "questions": len(inputs), "clips": len(clips),
                "source_videos": len(sources), "legacy_turns": sum(len(x) for x in turns.values()),
                "categories": dict(Counter(c["category"] for c in rows)),
                "statuses": dict(Counter(r["status"] for r in refs.values())),
                "source_group_counts": dict(Counter(c["source_id"] for c in rows)),
                "annotated_audio_ms": sum(c["duration_ms"] for c in rows),
                "multi_window_questions": sum(len(r["evidence_ms"]) > 1 for r in refs.values()),
                "gold_questions": 0}
    check(all(summary.get(k) == v for k, v in expected.items()), "Summary does not match data")
    return expected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=ROOT / "data")
    try:
        result = validate(parser.parse_args().data)
        print(f"PASS: {result['questions']} questions, {result['clips']} clips, "
              f"{result['source_videos']} source videos, {result['legacy_turns']} turns.")
    except (OSError, ValueError, TypeError, KeyError) as error:
        sys.exit(str(error))


if __name__ == "__main__":
    main()
