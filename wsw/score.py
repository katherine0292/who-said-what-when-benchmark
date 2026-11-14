"""Score structured predictions for the pilot's speaker and localization tasks."""
import argparse
import collections
import json
import statistics
import sys
import unicodedata

from .common import ROOT, read_rows, write_json


def valid_windows(windows, duration):
    if not isinstance(windows, list) or not windows:
        return False
    last = -1
    for pair in windows:
        if not isinstance(pair, list) or len(pair) != 2:
            return False
        start, end = pair
        if type(start) is not int or type(end) is not int or not (last <= start < end <= duration) or start < 0:
            return False
        last = end
    return True


def temporal_iou(prediction, reference):
    """IoU of time sets, so filling an intervening gap is penalized."""
    i = j = intersection = 0
    while i < len(prediction) and j < len(reference):
        a, b = prediction[i]
        c, d = reference[j]
        intersection += max(0, min(b, d) - max(a, c))
        if b <= d:
            i += 1
        else:
            j += 1
    union = sum(b - a for a, b in prediction + reference) - intersection
    return intersection / union if union else 0.0


def normalized_name(value):
    value = unicodedata.normalize("NFKC", value).casefold()
    return " ".join("".join(ch if ch.isalnum() else " " for ch in value).split())


def index(rows):
    result = {}
    for row in rows:
        key = row.get("id")
        if not isinstance(key, str) or key in result:
            raise ValueError(f"Missing or duplicate ID: {key!r}")
        result[key] = row
    return result


def average(values):
    values = list(values)
    return round(statistics.mean(values), 6) if values else None


def measure(rows):
    return {
        "n": len(rows),
        "coverage": average(r["submitted"] for r in rows),
        "valid_evidence_rate": average(r["valid_evidence"] for r in rows),
        "speaker_accuracy": average(r["speaker_correct"] for r in rows),
        "mean_tiou": average(r["tiou"] for r in rows),
        "recall_at_tiou_03": average(r["tiou"] >= 0.3 for r in rows),
        "recall_at_tiou_05": average(r["tiou"] >= 0.5 for r in rows),
        "recall_at_tiou_07": average(r["tiou"] >= 0.7 for r in rows),
        "speaker_and_tiou_05": average(r["speaker_correct"] and r["tiou"] >= 0.5 for r in rows),
        "identity_name_match_rate": average(r["identity_match"] for r in rows),
        "meaning_graded_coverage": average(r["meaning_score"] is not None for r in rows),
        "meaning_credit": average(r["meaning_score"] for r in rows if r["meaning_score"] is not None),
        "joint_pass": (average(r["speaker_correct"] and r["tiou"] >= 0.5
                               and r["meaning_score"] == 1 for r in rows)
                       if any(r["meaning_score"] is not None for r in rows) else None),
    }


def evaluate(inputs, references, clips, predictions, include_review=False, judgments=()):
    inputs, references, predictions, judgments = map(index, (inputs, references, predictions, judgments))
    if set(references) != set(inputs):
        raise ValueError("Inputs and references do not cover the same IDs")
    for rows in (predictions, judgments):
        unknown = rows.keys() - inputs.keys()
        if unknown:
            raise ValueError(f"Unknown IDs: {', '.join(sorted(unknown))}")
    clips = {row["clip_id"]: row for row in clips}
    results = []
    for qid in sorted(references):
        ref = references[qid]
        if ref["status"] == "needs_media_review" and not include_review:
            continue
        item, pred = inputs[qid], predictions.get(qid, {})
        clip = clips[item["clip_id"]]
        windows = pred.get("evidence_ms")
        valid = valid_windows(windows, item["duration_ms"])
        tiou = temporal_iou(windows, ref["evidence_ms"]) if valid else 0.0
        identity = pred.get("identity_name")
        meaning = None
        if qid in judgments:
            if not isinstance(pred.get("answer"), str) or not pred["answer"].strip():
                raise ValueError(f"{qid}: a meaning judgment requires a submitted answer")
            scores = judgments[qid].get("point_scores")
            if (not isinstance(scores, list) or len(scores) != len(ref["key_points"])
                    or any(type(s) not in (int, float) or s not in (0, 0.5, 1) for s in scores)):
                raise ValueError(f"{qid}: provide one 0, 0.5 or 1 per key point")
            contradiction = judgments[qid].get("material_contradiction")
            if type(contradiction) is not bool:
                raise ValueError(f"{qid}: material_contradiction must be boolean")
            meaning = 0.0 if contradiction else statistics.mean(scores)
        results.append({"id": qid, "submitted": qid in predictions, "category": clip["category"],
                        "source_id": clip["source_id"], "status": ref["status"],
                        "window_count": len(ref["evidence_ms"]), "valid_evidence": valid,
                        "speaker_correct": pred.get("speaker_id") == ref["speaker_id"],
                        "tiou": tiou, "identity_match": isinstance(identity, str)
                        and normalized_name(identity) == normalized_name(ref["identity_ref"]["name"]),
                        "meaning_score": meaning})
    groups = {}
    for key in ("category", "source_id", "status", "window_count"):
        grouped = collections.defaultdict(list)
        for row in results:
            grouped[str(row[key])].append(row)
        groups[key] = {k: measure(v) for k, v in sorted(grouped.items())}
    by_source = groups["source_id"]
    return {"scope": "all_pilot_including_review" if include_review else "text_aligned_pilot",
            "overall": measure(results), "slices": groups,
            "source_macro_mean_tiou": average(v["mean_tiou"] for v in by_source.values()),
            "source_macro_joint_speaker_time": average(v["speaker_and_tiou_05"] for v in by_source.values()),
            "items": results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("predictions")
    parser.add_argument("--data", default=ROOT / "data")
    parser.add_argument("--judgments", help="Optional human point scores, one JSON object per line")
    parser.add_argument("--include-review", action="store_true")
    parser.add_argument("--out")
    args = parser.parse_args()
    from pathlib import Path
    try:
        data = Path(args.data)
        result = evaluate(*(read_rows(data / f"{name}.jsonl") for name in ("inputs", "references", "clips")),
                          read_rows(args.predictions), args.include_review,
                          read_rows(args.judgments) if args.judgments else ())
        if args.out:
            write_json(args.out, result)
        print(json.dumps({"scope": result["scope"], **result["overall"]}, ensure_ascii=False, indent=2))
    except (OSError, ValueError, KeyError) as error:
        sys.exit(str(error))


if __name__ == "__main__":
    main()
