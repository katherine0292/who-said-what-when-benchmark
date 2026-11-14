# Who Said What When

Given an interview audio clip and a natural-language question, a model must identify **who spoke, what they said, and which time intervals support the answer**. A single answer can require multiple noncontiguous intervals. This repository includes an annotation handbook, a data card, a reproducible conversion and scoring workflow, and a pilot dataset derived from two rounds of annotations.

**Version `0.1.0-pilot`** contains 25 English questions, 25 audio clips from 5 source videos, and 178 annotated turns. The clips total approximately 94 minutes and 47 seconds. Eighteen questions have been aligned against the source annotations and seven are flagged for priority audio review. Independent listening review and a held-out test set are planned for a subsequent release.

## What the dataset measures

The benchmark measures speaker attribution, comprehension, and temporal grounding in conversations. In Round 1, annotators record speakers, turns, transcripts, timestamps, and delivery. In Round 2, they write a question with one intended answer and link it to the turns that support it. The current material covers food and diner culture, identity and psychological adaptation, adolescent development, perspectives on influence and decision-making, and personal initiative and professional roles. The annotations attribute claims to the speakers who made them.

A fluent meeting summary can assign a guest's opinion to the host or give a timestamp that takes the listener to the wrong passage. Scoring attribution, meaning, and timing separately helps diagnose these errors in meeting notes, interview search, and audio assistants.

## Repository guide

| Resource | Contents |
| --- | --- |
| [Data card](docs/DATA_CARD.md) | Purpose, topic coverage, collection process, uses, and limitations |
| [Annotation handbook](docs/ANNOTATION_GUIDE.md) | Clip selection, turn annotation, question writing, independent review, and acceptance criteria |
| [Benchmark protocol](docs/BENCHMARK_PROTOCOL.md) | Input conditions, data splits, metrics, baselines, and release criteria |
| [Data format and examples](docs/FORMAT.md) | Model inputs, reference answers, prediction format, and migration fields |
| [Migration audit](docs/MIGRATION_AUDIT.md) | Corrections and the seven items that need priority listening review |
| [Inputs](data/inputs.jsonl), [references](data/references.jsonl), and [summary](data/summary.json) | The 25 converted pilot items |
| [JSON Schemas](schemas/) | Machine-readable formats for annotation and evaluation files |

## Quick start

Use Python 3.10 or later. Validation and scoring require only the standard library and run offline from the repository root.

```bash
python3 -m wsw.validate
python3 -m unittest discover -s tests -v
python3 -m wsw.score examples/whole_clip.jsonl
python3 -m wsw.score examples/middle_20pct.jsonl --out /tmp/wsw-report.json
```

To rebuild the pilot from the original annotation and media folder, use `afinfo` on macOS or `ffprobe` on other platforms. MP3 duration estimates can vary slightly by tool.

```bash
python3 -m wsw.convert "/path/to/original-benchmark" --out /tmp/wsw-rebuilt
python3 -m wsw.validate --data /tmp/wsw-rebuilt
```

For a model run, provide each row from `data/inputs.jsonl` with its matching MP3. The local media manifest maps clip IDs to filenames and checksums. References, turn records, source URLs, and audit logs are evaluator materials. Original media, verbatim transcripts, and source answers are kept locally. The converter writes the source annotations and media index to `data/local/`, which Git ignores. The source materials have no declared open redistribution license.
