# Who Said What When

**Speaker-attributed, temporally grounded question answering for conversational audio.**

![Who Said What When — conversational voices linked to supporting audio evidence](assets/who-said-what-when-poster.png)

Given an interview or podcast clip and a natural-language question, a model must identify **who spoke**, explain **what they meant**, and locate **when the supporting evidence occurs**. An answer may depend on several noncontiguous passages.

This repository provides a pilot dataset, a two-round annotation workflow, structured data formats, validation tools, and a reproducible scorer. It supports research on conversational audio understanding and error analysis for source-linked meeting notes, interview search, and audio assistants.

[Interactive walkthrough](https://katherine0292.github.io/who-said-what-when-benchmark/) · [Data card](docs/DATA_CARD.md) · [Annotation guide](docs/ANNOTATION_GUIDE.md) · [Evaluation protocol](docs/BENCHMARK_PROTOCOL.md)

> **Release status: `0.1.0-pilot`.** The default evaluation uses 18 text-aligned items; 7 additional items require priority audio review. All 25 await independent listening review. The pilot supports workflow validation and error analysis; it does not yet provide a gold test set or a basis for reliable model rankings.

## Why this benchmark

A useful audio answer preserves the relationship between a claim, its speaker, and its source. A summary can sound plausible while assigning a guest's view to the host, reversing a qualification, or sending the listener to the wrong passage.

Who Said What When evaluates these dimensions separately and together:

| Dimension | Required behavior | Error it reveals |
| --- | --- | --- |
| **Who** | Identify the speaker within the clip | Confusing a question, paraphrase, or quotation with the original speaker's claim |
| **What** | Answer the question while preserving the relevant meaning | Losing negation, conditions, stance, or causal direction |
| **When** | Return the intervals that support the answer | Selecting irrelevant audio or omitting a necessary passage |

The main track uses **audio and a question**. ASR and question-only controls help isolate the contribution of audio evidence. Named identity and perceived delivery are separate, optional conditions. See the [protocol](docs/BENCHMARK_PROTOCOL.md) for input rules.

## Pilot at a glance

| Property | Current release |
| --- | --- |
| Questions / audio clips | 25 / 25 |
| Source videos | 5 |
| Annotated speaker turns | 178 |
| Language | English |
| Total clip duration | Approximately 94 minutes 47 seconds, including overlapping source material |
| Speakers per clip | 2–3 |
| Questions with multiple evidence intervals | 4 |
| Review status | 18 `text_aligned`; 7 `needs_media_review`; 0 gold items |
| Data split | All items are `pilot`; no held-out test set |

Topics span food culture, identity and psychological adaptation, adolescent development, influence and decision-making, and personal initiative. Category coverage is concentrated: 23 items are Education & Knowledge and 2 are Lifestyle & Daily. Claims in the material are attributed to their speakers. See the [data card](docs/DATA_CARD.md) for provenance and scope.

## Quick start

**Requirements:** Python 3.10 or later. Validation, baseline generation, and scoring use only the Python standard library. The commands below run without downloading audio or invoking a model.

```bash
git clone https://github.com/katherine0292/who-said-what-when-benchmark.git
cd who-said-what-when-benchmark

# Check data integrity and run the existing test suite.
python3 -m wsw.validate
python3 -m unittest discover -s tests -v

# Score the bundled diagnostic predictions.
python3 -m wsw.score examples/whole_clip.jsonl
python3 -m wsw.score examples/middle_20pct.jsonl --out /tmp/wsw-report.json
```

The scorer evaluates the 18 text-aligned items by default. To include the 7 flagged items for a workflow check, add `--include-review`; report that scope explicitly.

## Run an evaluation

### 1. Prepare model inputs

Pair each row of [`data/inputs.jsonl`](data/inputs.jsonl) with its matching MP3 using the local media manifest. Model-facing fields are the item ID, clip ID, duration, language, and question. Number speakers `spk_01`, `spk_02`, and so on in order of first identifiable speech.

Keep references, turn records, source URLs, identities, and audit logs with the evaluator. Use neutral audio filenames that do not reveal names or original video IDs. If a model emits its own anonymous speaker IDs, map them once by time without consulting reference answers and document the procedure.

**Audio is not bundled in this repository.** Model inference requires separately obtained source media. The converter creates a local media manifest from an available original annotation and media folder; see [rebuilding the data](#rebuild-from-source-annotations).

### 2. Write predictions

Submit UTF-8 JSONL with one prediction per item. This example illustrates the structure using `wsw_0018`, whose evidence spans two turns separated by another speaker's acknowledgment:

```json
{"id":"wsw_0018","speaker_id":"spk_02","answer":"A situation cannot be changed and must be accepted. A problem has a solution, even if it is uncomfortable.","evidence_ms":[[10000,26000],[27000,59000]]}
```

Evidence uses clip-local, half-open intervals `[start_ms, end_ms)` in integer milliseconds. Intervals must be sorted, non-overlapping, positive in length, and within the clip duration. They describe the actual supporting passages, including gaps between them. Legacy annotations retain one-second resolution despite storage in milliseconds.

Only `id` is required by the prediction schema. Missing speaker or evidence fields receive zero on the corresponding metrics. Include `answer` for meaning evaluation; `identity_name` is an optional diagnostic. Unknown or duplicate IDs cause an error. See [formats and examples](docs/FORMAT.md) and the [prediction schema](schemas/prediction.schema.json).

### 3. Score speaker, time, and meaning

```bash
python3 -m wsw.score predictions.jsonl --out /tmp/wsw-results.json
```

Speaker and time metrics are automatic. **Meaning requires a separate judgments file** with one score per reference key point, using `0`, `0.5`, or `1`, plus a material-contradiction flag. For example:

```json
{"id":"wsw_0018","point_scores":[1,1],"material_contradiction":false}
```

```bash
python3 -m wsw.score predictions.jsonl --judgments judgments.jsonl --out /tmp/wsw-results.json
```

| Metric | Interpretation |
| --- | --- |
| Speaker Accuracy | Fraction of evaluated items with the correct clip-local speaker ID |
| Mean temporal IoU (tIoU) | Intersection duration divided by union duration of predicted and reference time sets, averaged per item |
| R@1 at tIoU 0.3 / 0.5 / 0.7 | Fraction of items whose prediction reaches each localization threshold |
| Speaker + Time | Correct speaker and tIoU ≥ 0.5 |
| Meaning Credit | Mean key-point credit across graded items; a material contradiction makes the item's meaning score zero |
| Joint Pass | Correct speaker, tIoU ≥ 0.5, and full meaning credit |

tIoU operates on the union of the actual intervals, so including an unsupported gap reduces the score. Reports also include submission coverage, valid evidence rate, grading coverage, source-level macro averages, and breakdowns by category, source, review status, and interval count.

Joint Pass uses all evaluated items as its denominator. With partial meaning grading, it is a lower bound; with no meaning judgments, it is `null`. Report grading coverage alongside meaning and joint results. See the [protocol](docs/BENCHMARK_PROTOCOL.md) for grading and reporting requirements.

## Diagnostic baselines

Both bundled baselines predict `spk_01` and use only clip duration. They provide a reproducibility check and reveal how fixed time guesses behave. Neither generates a free-text answer.

Results on the **18 text-aligned items**:

| Baseline | Speaker Accuracy | Mean tIoU | Speaker + Time |
| --- | ---: | ---: | ---: |
| First speaker + entire clip | 38.89% | 0.3043 | 16.67% |
| First speaker + middle 20% | 38.89% | 0.1098 | 0.00% |

Recreate a baseline from model-facing metadata:

```bash
python3 -m wsw.baseline --mode whole --out /tmp/wsw-whole.jsonl
python3 -m wsw.score /tmp/wsw-whole.jsonl
```

Predicting the entire clip can receive credit when reference evidence is long. Interpret localization scores alongside evidence-length breakdowns and joint evaluation.

## Annotation and data quality

**Round 1** records speakers, turns, transcripts, timestamps, and delivery. **Round 2** creates questions and links answer key points to supporting turns. Migration reconciles the submitted records, normalizes IDs and clocks, and records repairs in an auditable form.

`text_aligned` means aligned against the submitted annotation text; it does not indicate independent audio verification. The 7 flagged items have timing or clip-version conflicts documented in the [migration audit](docs/MIGRATION_AUDIT.md).

A gold release requires independent listening review, verification of minimal evidence and speaker attribution, resolution of media/version conflicts, documented permissions, and frozen splits. Future splits must group related source material to prevent leakage. The proposed 800-item expansion and 70/15/15 split are planning targets, not available data.

## Repository guide

| Path | Contents |
| --- | --- |
| [`data/`](data/) | Pilot inputs, references, clips, turn metadata, migration audit, and summary |
| [`wsw/`](wsw/) | Conversion, validation, diagnostic baseline generation, and scoring tools |
| [`schemas/`](schemas/) | JSON Schemas for data, predictions, and judgments |
| [`examples/`](examples/) | Baseline predictions and saved reports |
| [`tests/`](tests/) | Integrity, scoring, interval, and submission tests |
| [Annotation guide](docs/ANNOTATION_GUIDE.md) | Annotation and independent-review procedures |
| [Benchmark protocol](docs/BENCHMARK_PROTOCOL.md) | Tracks, metrics, splits, baselines, and release criteria |
| [Data card](docs/DATA_CARD.md) | Motivation, provenance, intended uses, and limitations |
| [Data format](docs/FORMAT.md) | Fields, clocks, and submission formats |
| [Migration audit](docs/MIGRATION_AUDIT.md) | Migration decisions and priority audio-review queue |

## Rebuild from source annotations

Rebuilding requires the original annotation and media folder, which is not included. The converter uses `afinfo` on macOS or `ffprobe` on other platforms to estimate audio duration; estimates may differ slightly between tools.

```bash
python3 -m wsw.convert "/path/to/original-benchmark" --out /tmp/wsw-rebuilt
python3 -m wsw.validate --data /tmp/wsw-rebuilt
```

The converter also writes original annotations and a media manifest under the output's `local/` directory. In the repository, `data/local/` is Git-ignored.

## Access, limitations, and reproducibility

The repository includes edited questions, reference key points, and turn metadata. Original media, verbatim transcripts, and source answers remain local. Source materials have no declared open redistribution license; their public availability does not establish permission to redistribute them.

The pilot is limited to English, five source videos, and a narrow topic distribution. Some sources share a host, and public source material may occur in model pretraining. These constraints limit generalization claims and model comparisons. Voiceprint identification and personal attribute inference are outside the task scope.

For each reported run, record the dataset version and commit, evaluation scope, model version, prompt, audio preprocessing, sampling settings, speaker-ID mapping, external-search policy, repeat-run policy, and human-grading coverage. Record item IDs and reasons when changing questions, references, evidence, or scoring rules.
