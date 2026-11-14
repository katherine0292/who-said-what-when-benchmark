"""Rebuild the pilot from the submitted legacy directory (Python 3.10+)."""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
from urllib.parse import parse_qs, urlparse

from .common import CATEGORIES, ROOT, VERSION, timestamp_ms, write_json, write_rows
from .editorial import EDITS, REVIEW, TONE


def sha256(path):
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest() if hasattr(hashlib, "file_digest") else _hash_chunks(handle)


def _hash_chunks(handle):
    digest = hashlib.sha256()
    for chunk in iter(lambda: handle.read(1024 * 1024), b""):
        digest.update(chunk)
    return digest.hexdigest()


def load_legacy(path):
    text = path.read_text(encoding="utf-8-sig")
    repaired, count = re.subn(r'("video_id":\s*"v[45])”(?=,)', r'\1"', text)
    return json.loads(repaired), count


def single(value):
    if isinstance(value, list):
        value, = value
    return value


def audio_ms(path):
    if shutil.which("afinfo"):
        output = subprocess.check_output(["afinfo", str(path)], text=True)
        value = re.search(r"estimated duration:\s+([\d.]+)", output)[1]
    elif shutil.which("ffprobe"):
        output = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries",
                                          "format=duration", "-of", "json", str(path)], text=True)
        value = json.loads(output)["format"]["duration"]
    else:
        raise SystemExit("Source conversion needs afinfo (macOS) or ffprobe (Linux/Windows).")
    return round(float(value) * 1000)


def voice_traits(text):
    # Legacy Age is intentionally kept only in the local source archive.
    names = {"accent": "accent_impression", "timbre": "timbre", "prosody": "prosody",
             "volume": "relative_volume", "rhythm": "rhythm"}
    traits = {}
    for part in text.split(";"):
        key, sep, value = part.partition(":")
        canonical = names.get(key.strip().lower())
        if sep and canonical and value.strip():
            traits[canonical] = value.strip()
    return traits


def windows(turns):
    result = []
    for turn in turns:
        start, end = turn["start_ms"], turn["end_ms"]
        if start is None or end is None:
            raise ValueError("An evidence turn lacks a usable clock")
        if result and start <= result[-1][1]:
            result[-1][1] = max(result[-1][1], end)
        else:
            result.append([start, end])
    return result


def convert(source, out):
    if (source / "视频标注").is_dir():
        source = source / "视频标注"
    aggregates = {}
    for round_no in (1, 2):
        path, = source.glob(f"*_round{round_no}.json")
        aggregates[round_no] = load_legacy(path)
    aggregate_qa = {r["id"]: r for r in aggregates[2][0]}
    media_dirs = {p.parent for p in source.rglob("*") if p.suffix.lower() == ".mov"}
    clips, turns_out, inputs, labels, archive, audits, media_rows = [], [], [], [], [], [], []
    topic_seen = collections.Counter()
    for directory in sorted(media_dirs, key=lambda d: tuple(map(int, re.findall(r"\d+", d.name)))):
        path1, path2 = sorted(directory.glob("*.json"))
        raw1, repair1 = load_legacy(path1)
        raw2, repair2 = load_legacy(path2)
        first, second = single(raw1), single(raw2)
        legacy_id = second["id"]
        number = int(legacy_id.split("_")[-1])
        qid = f"wsw_{number:04d}"
        clip_id = directory.name
        category = first["category"]
        if category not in CATEGORIES:
            raise ValueError(f"Unknown category {category!r}")
        url = first["video_link"].strip()
        video_token = parse_qs(urlparse(url).query)["v"][0]
        source_id = f"yt:{video_token}"
        match1, = [r for r in aggregates[1][0]
                   if all(r[k] == first[k] for k in ("video_id", "topic", "browser_start_timestamp", "browser_end_timestamp"))]
        match2 = aggregate_qa[legacy_id]
        audio, = [p for p in directory.iterdir() if p.suffix.lower() == ".mp3"]
        video, = [p for p in directory.iterdir() if p.suffix.lower() == ".mov"]
        length = audio_ms(audio)
        source_window = [timestamp_ms(first[k]) for k in ("browser_start_timestamp", "browser_end_timestamp")]
        delta = length - (source_window[1] - source_window[0])
        flags = list(REVIEW.get(clip_id, []))
        if (abs(delta) > 1500) != ("origin_duration_mismatch" in flags):
            raise ValueError(f"{clip_id}: duration audit changed (delta {delta} ms)")
        speakers = {}
        turns = []
        for row in first["speakers"]:
            name = row["speaker"].strip()
            speaker = speakers.setdefault(name, f"spk_{len(speakers) + 1:02d}")
            start = timestamp_ms(row["start_time"])
            raw_end = row.get("end_time")
            try:
                end = timestamp_ms(raw_end) if raw_end else None
            except ValueError:
                end = None
            clock = ("invalid_legacy_clock" if end is None or start >= end else
                     "exceeds_audio" if end > length + 1000 else "legacy")
            turns.append({"clip_id": clip_id, "turn_id": row["turns"], "speaker_id": speaker,
                          "start_ms": start, "end_ms": end, "clock_status": clock})
        turns_out += turns
        question, key_points, override, note = EDITS[number]
        original_ids = second["turn_id"] if isinstance(second["turn_id"], list) else [second["turn_id"]]
        selected = override if override is not None else original_ids
        targets = [next(t for t in turns if t["turn_id"] == i) for i in selected]
        evidence = windows(targets)
        speaker_id, = {t["speaker_id"] for t in targets}
        name = next(name for name, sid in speakers.items() if sid == speaker_id)
        if name != second["speaker"]:
            raise ValueError(f"{clip_id}: reference speaker mismatch")
        draft = "needs_media_review" if flags else "text_aligned"
        source_turn = next(t for t in first["speakers"] if t["turns"] == selected[0])
        inputs.append({"id": qid, "clip_id": clip_id, "duration_ms": length,
                       "language": "en", "question": question})
        labels.append({"id": qid, "clip_id": clip_id, "speaker_id": speaker_id,
                       "identity_ref": {"name": name, "role": source_turn["identity"]},
                       "voice_ref": voice_traits(source_turn["audio_speaker_id"]),
                       "tone_ref": TONE[number], "tone_source": second["emotion"],
                       "key_points": key_points, "evidence_ms": evidence, "turn_ids": selected,
                       "status": draft, "split": "pilot"})
        clips.append({"clip_id": clip_id, "source_id": source_id, "source_url": url,
                      "source_window_reported_ms": source_window, "duration_ms": length,
                      "category": category, "topic": first["topic"], "language": "en",
                      "speaker_count": len(speakers), "turn_count": len(turns), "status": draft,
                      "review_flags": flags, "split": "pilot"})
        topic_seen[category] += 1
        audit_turn = next(t for t in first["speakers"] if t["turns"] == original_ids[0])
        audits.append({"id": qid, "clip_id": clip_id, "legacy_id": legacy_id,
                       "legacy_media_id": second["media_id"], "legacy_turn_ids": original_ids,
                       "legacy_evidence_envelope_ms": [timestamp_ms(second[k]) for k in ("start_time", "end_time")],
                       "canonical_turn_ids": selected, "round1_quote_repair": repair1,
                       "aggregate_round1_fields_changed": sorted(k for k in first.keys() | match1.keys() if first.get(k) != match1.get(k)),
                       "aggregate_round2_fields_changed": sorted(k for k in second.keys() | match2.keys() if second.get(k) != match2.get(k)),
                       "legacy_transcript_matches_first_target_turn": audit_turn["transcription"] == second["transcription"],
                       "origin_minus_audio_ms": -delta, "flags": flags, "editorial_note": note})
        archive.append({"id": qid, "clip_id": clip_id, "round1": raw1, "round2": raw2,
                        "round1_aggregate": match1, "round2_aggregate": match2})
        media_rows.append({"clip_id": clip_id, "audio_relative_path": audio.relative_to(source).as_posix(),
                           "video_relative_path": video.relative_to(source).as_posix(),
                           "audio_sha256": sha256(audio), "video_sha256": sha256(video),
                           "audio_bytes": audio.stat().st_size, "video_bytes": video.stat().st_size})

    if sorted(row["id"] for row in labels) != [f"wsw_{i:04d}" for i in EDITS]:
        raise ValueError("Legacy inputs differ from this migration's expected QA IDs.")
    out.mkdir(parents=True, exist_ok=True)
    for name, rows, sort_key in (("inputs", inputs, "id"), ("references", labels, "id"), ("clips", clips, None),
                                 ("turns", turns_out, None), ("migration_audit", audits, "id")):
        write_rows(out / f"{name}.jsonl", sorted(rows, key=lambda row: row[sort_key]) if sort_key else rows)
    local = out / "local"
    write_rows(local / "legacy_rounds.jsonl", sorted(archive, key=lambda row: row["id"]))
    write_rows(local / "media_manifest.jsonl", media_rows)
    write_json(out / "summary.json", {
        "version": VERSION, "questions": len(labels), "clips": len(clips),
        "source_videos": len({c["source_id"] for c in clips}), "legacy_turns": len(turns_out),
        "source_group_counts": {s: sum(c["source_id"] == s for c in clips) for s in sorted({c["source_id"] for c in clips})},
        "categories": dict(topic_seen), "statuses": dict(collections.Counter(l["status"] for l in labels)),
        "annotated_audio_ms": sum(c["duration_ms"] for c in clips),
        "local_media_bytes": sum(r["audio_bytes"] + r["video_bytes"] for r in media_rows),
        "legacy_round1_quote_repairs_per_clip": sum(r["round1_quote_repair"] for r in audits),
        "legacy_round1_quote_repairs_in_aggregate": aggregates[1][1],
        "legacy_time_resolution_ms": 1000,
        "multi_window_questions": sum(len(l["evidence_ms"]) > 1 for l in labels),
        "gold_questions": 0,
    })


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Original benchmark folder or its 视频标注 subfolder")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    convert(args.source, args.out)


if __name__ == "__main__":
    main()
