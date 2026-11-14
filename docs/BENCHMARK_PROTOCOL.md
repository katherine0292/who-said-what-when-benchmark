# Benchmark Protocol

## 1. Task and input conditions

In the main task, the model receives a clipped English conversation and a question that withholds the answer. It returns a clip-local speaker ID, a free-text answer, and one or more evidence intervals. Assign speaker IDs in order of first identifiable speech. If the model emits its own anonymous IDs, map them once by time before evaluation and report the mapping procedure. Reference answers are held out of this mapping.

| Condition | Model inputs | Purpose |
| --- | --- | --- |
| Audio-only main track | Audio, question, clip duration, and speaker numbering rule | Evaluate attribution, meaning, and temporal grounding from audible evidence |
| ASR control | A standardized automatic transcript with timestamps and the same question | Measure performance with text input. Report the ASR version and whether diarization was supplied. |
| Question-only control | Question and clip duration | Check how much models can infer from question wording, general knowledge, or fixed time guesses |
| Identity extension | Audio, question, and a verified roster of names and roles, with the voice-to-name mapping withheld | Evaluate named speaker attribution given the roster |
| Optional delivery diagnostic | Audio and a dedicated question that withholds the delivery label | Assess perceived delivery and report inter-annotator agreement separately |

Build model prompts from `data/inputs.jsonl` and the matching audio. Remove names and original video IDs from audio filenames. The evaluation team retains source URLs, topics, references, transcripts, turns, candidate answers, and annotation logs. Public source material can appear in model pretraining, which can affect results. Report the model version, audio preprocessing, prompt, sampling settings, external-search policy, and repeat-run policy.

## 2. Data splits and scale

All current items belong to `pilot`. For formal splits, group by source video and identify shared programs, speakers, and repeated content. Keep clips from the same source, near duplicates, and overlapping source intervals in the same split. A speaker generalization test should hold out speakers. A program generalization test should hold out programs. If both constraints cannot be met in one split, document and report the two settings separately.

For the proposed 800-item expansion, 70% development, 15% validation, and 15% held-out test are planning targets. Adjust them to the number of independent groups and category coverage. Report counts by source group, speaker count, evidence length, evidence interval count, language, and category. Add independent sources to improve coverage. Freeze the test media, questions, references, and rules, and keep the held-out answers with the evaluation team.

## 3. Automatic and human scoring

| Metric | Definition |
| --- | --- |
| Speaker Accuracy | Proportion of evaluated items with the correct clip-local `speaker_id` |
| Mean tIoU | Mean per-item ratio of the intersection duration to the union duration of predicted and reference time sets |
| R@1 at tIoU 0.3, 0.5, and 0.7 | Proportion of items whose single prediction reaches each threshold |
| Speaker + Time | Proportion with the correct speaker and tIoU of at least 0.5 |
| Meaning Credit | Mean across human-scored items, with each key point awarded 0, 0.5, or 1 and a material contradiction reducing the item to zero. Report grading coverage. |
| Joint Pass | Proportion with correct speaker, tIoU of at least 0.5, and full meaning credit. The denominator is all evaluated items, so partial human grading yields a lower bound. With zero graded items the value is null. |
| Identity Name Match | Optional exact match after name normalization. Roles, aliases, and delivery do not contribute to this diagnostic. |
| Coverage and Valid Evidence Rate | Proportions with a submission and with correctly formatted in-bounds evidence, respectively |

Compute tIoU over the union of the actual intervals in each set. For reference intervals of 10–26 seconds and 27–59 seconds, predicting 10–59 seconds yields 48/49, or approximately 0.980. Extra intervening time reduces the score. Evidence uses sorted, non-overlapping, positive-length integer-millisecond intervals bounded by the clip duration. Unknown or duplicate IDs cause an error. Missing predictions and invalid evidence receive zero for the corresponding metrics.

Report overall item averages, source-level macro averages for tIoU and Speaker + Time, and breakdowns by category, source, review status, and number of reference intervals. Include counts. For a larger held-out evaluation, use source-group bootstrap sampling for confidence intervals and report the number of independent groups. The five pilot sources offer limited support for model rankings.

Award 1 to a fully expressed and evidence-consistent key point, 0.5 to a partly correct or vague one, and 0 to a missing or wrong one. Accept equivalent wording. Reversing a speaker's stance, dropping a key negation, or inventing a causal claim counts as a material contradiction. Speaker identity and time are scored separately. A formal evaluation should use blinded reviewers or a calibrated grading process with sampled human checks. The scorer accepts a JSONL file of human judgments.

## 4. Baselines

Both baselines always predict `spk_01` and use only the clip duration. One predicts the entire clip and the other predicts its middle 20%. Results below use the 18 items with text-aligned references.

| Baseline | Speaker Accuracy | Mean tIoU | Speaker + Time |
| --- | ---: | ---: | ---: |
| First speaker and entire clip | 38.89% | 0.3043 | 16.67% |
| First speaker and middle 20% | 38.89% | 0.1098 | 0.00% |

These baselines leave the free-text answer blank. An entire-clip prediction can score on long turns. Short-evidence breakdowns and joint scoring help detect this effect. Future runs can compare transcript retrieval with audio-only models on the same split and report failures in speaker attribution, answer meaning, and evidence localization.

## 5. Gold release criteria

1. Verify each clip version, its source offset, and its local SHA-256. Resolve priority audio review findings.
2. Have two reviewers independently verify meaning and minimal evidence for each gold item. Record any adjudication.
3. Check duplicates, overlap, shared speakers and programs, and answer leakage. Freeze the splits.
4. Document data and media permissions and how evaluators can replay the evidence. Use only the held-out test set for any leaderboard.
5. Publish the schemas, data card, evaluation commands, baselines, topic and item distributions, and a fixed version and commit hash.

For related temporal localization and speaker attribution tasks, see [Ego4D Episodic Memory](https://ego4d-data.org/docs/benchmarks/episodic-memory/) and [NIST Rich Transcription](https://www.nist.gov/publications/rich-transcription-2007-meeting-recognition-evaluation).
