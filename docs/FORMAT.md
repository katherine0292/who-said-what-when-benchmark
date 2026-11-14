# Data Format and Field Mapping

JSONL files are UTF-8, with one JSON object per line. The local clip clock starts at 0 and uses half-open integer-millisecond intervals `[start_ms, end_ms)`. Legacy labels retain one-second resolution after unit conversion. Reported source-video timestamps use a separate clock. Verify source alignment before deriving absolute evidence timestamps.

| File | Keys and relationships | Contents |
| --- | --- | --- |
| `data/clips.jsonl` | `clip_id`. Multiple clips may share a `source_id`. | Source URL and reported window, estimated audio duration, category, topic, speaker and turn counts, and review status |
| `data/turns.jsonl` | `clip_id` and `turn_id` | Speaker ID, clip-local turn boundaries, and clock status for the evaluator |
| `data/inputs.jsonl` | `id`, with `clip_id` as a foreign key | Question, language, and duration. Supply each row with its matching audio. |
| `data/references.jsonl` | `id`, linked to `clip_id` and `turn_ids` | Speaker ID, identity, voice traits, delivery, answer key points, evidence intervals, and review status |
| `data/migration_audit.jsonl` | `id` | Original IDs, clocks and turns, aggregate differences, repairs, and review flags |
| `data/summary.json` | Dataset version | Item and source counts, categories, and review status totals |
| `data/local/legacy_rounds.jsonl` | `id` | Local converter output containing original-language annotations, with JSON quote syntax repaired, and both aggregate and per-clip versions |
| `data/local/media_manifest.jsonl` | `clip_id` | Local converter output with relative paths, file sizes, and SHA-256 checksums |

`identity_ref` contains the name and English role description derived from the source annotation. `voice_ref` retains audible timbre, prosody, relative loudness, rhythm, and optional accent impressions. The original `voice_answer` and `identity_answer` are stored locally. Their shared meaning and timing are represented in `key_points` and `evidence_ms`. The optional delivery fields are `tone_ref`, the edited candidate label, and `tone_source`, the original label. The automatic main metrics exclude both delivery fields.

| Legacy field | Converted field and handling |
| --- | --- |
| `video_id` and `media_id` | Use the clip directory name for `clip_id` and derive `source_id` from the original video link. Keep legacy IDs in the audit. |
| `browser_start_timestamp` and `browser_end_timestamp` | Preserve as `source_window_reported_ms` and flag alignment issues. |
| `topic` and the target turn's `identity` | Use curated English translations for the released topic and role. Keep original text in the local archive. |
| `speakers[].turns` and `speaker` | Map to `turn_id` and clip-local `speaker_id`. Identity and voice traits are evaluator fields. |
| `start_time` and `end_time` | Store as `start_ms` and `end_ms` for turns. Use `evidence_ms` for item evidence. |
| `question` and `transcription` | Rewrite questions to reduce leakage. Keep verbatim source transcripts locally for evidence review. |
| Round 2 `turn_id` | Convert to a `turn_ids` array. Evidence uses the union of the referenced turn intervals. |

The prediction below targets `wsw_0018`, which has two evidence intervals separated by a one-second interjection from another speaker.

```json
{
  "id": "wsw_0018",
  "speaker_id": "spk_02",
  "evidence_ms": [[10000, 26000], [27000, 59000]],
  "answer": "A situation cannot be changed and must be accepted. A problem has a solution, even if it is uncomfortable."
}
```

Prediction JSONL requires `id`. A missing `speaker_id` or `evidence_ms` earns zero for the corresponding metric. Both `identity_name` and `answer` are optional. To score meaning, submit a separate judgments file with one rating per reference key point.

```json
{"id":"wsw_0018","point_scores":[1,1],"material_contradiction":false}
```

```bash
python3 -m wsw.score predictions.jsonl --judgments judgments.jsonl --out results.json
```

See `schemas/` for machine-readable row schemas. Run `python3 -m wsw.validate` to check cross-file IDs, evidence-to-turn links, duration bounds, status, and source grouping. To support finer evidence spans in a later release, record sub-turn intervals and update the validator to check their containment.
