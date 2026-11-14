# Data Card

## 1. Annotation scope

The source material consists of excerpts from English-language interviews and podcasts, along with two rounds of annotations. A **clip** is one extracted audio file. A **turn** is a continuous contribution by one speaker. An **evaluation item** links one question to one or more supporting turns. Annotators can consult the source video to verify identities. The main task uses audible evidence.

**Who** identifies the speaker within the clip. **What** captures the meaning, position, or question expressed. **When** identifies the audio intervals where a reviewer can hear the supporting evidence. Perceived delivery and voice traits provide optional diagnostics. Names and program roles are evaluated under a separate input condition. The quantum-technology example in the original instructions illustrates the format and is outside the pilot dataset.

## 2. Topic coverage

| Source group | Questions | Topics |
| --- | ---: | --- |
| v1 | 2 | Food culture, the inclusiveness of diners, and trust through shared meals |
| v2 | 5 | Personal history, self-affirmation, identity foreclosure, and cognitive reappraisal |
| v3 | 5 | Adolescent identity, self-esteem research, stereotypes, and belonging |
| v4 | 5 | Interviewee accounts of social scripts, perception, influence, and authority |
| v5 | 8 | Taking action, situations versus problems, and consistency in professional roles |

There are 23 Education & Knowledge items and 2 Lifestyle & Daily items. Clips run approximately 3:00 to 4:58. Two clips have three speakers and the other 23 have two. Some sources share a host. The original instructions proposed 800 questions as an expansion target. The 25-question pilot covers a limited range of languages, categories, programs, and speakers. Total duration sums the local clips, including any overlapping source material.

## 3. Motivation and intended uses

Automatic speech recognition supplies words, diarization tracks speaker changes, and question answering summarizes meaning. Many applications need all three. In a meeting, for example, the host might ask about a delay while two participants take opposite positions. A keyword search for “delay” cannot establish who proposed it or where the rationale appears.

| Failure to diagnose | Evidence to check | Application |
| --- | --- | --- |
| The host's paraphrase is attributed to the guest | Speaker assignment and the distinction between questions, quotations, and assertions | Interview indexes and source-linked meeting notes |
| The summary reverses a key qualification | Key points, causal direction, negation, and conditions | Assistant evaluation and quality assurance |
| The answer's timestamp is hard to verify | The shortest intervals that support the answer and whether any necessary turns were missed | Audio retrieval and playback navigation |
| A delivery cue is treated as identity or an internal emotion | Audible traits, separately documented names and roles, and uncertain cases | Audio comprehension diagnostics |

Comparing audio and ASR conditions can show how results change when prosody and speaker-change cues are unavailable. Speaker accuracy, meaning scores, and temporal intersection over union help distinguish transcription, diarization, retrieval, and question-answering errors. The pilot supports workflow checks and error analysis. Its size and source concentration limit population-level claims and model comparisons.

## 4. Collection and review status

- The submission contains 25 MOV files, 25 MP3 files, 50 per-clip JSON files, and 2 aggregate JSON files. The original workflow proposed model-assisted drafts and human refinement. The files provide no per-item reviewer history, inter-annotator agreement results, or permissions records.
- Migration repaired JSON syntax, reconciled IDs, compared aggregate and per-clip records, estimated MP3 duration, and revised questions, key points, and supporting turns against the submitted text. The 178 turn records retain speaker links and timing information. Original annotation text is preserved in the local archive.
- The default evaluation uses 18 `text_aligned` questions. Seven `needs_media_review` questions have timing or version conflicts that warrant priority review. All 25 await independent listening review before gold release.
- Names and roles come from the submitted annotations and await independent verification against program sources. Delivery and voice traits are perceived attributes, some inherited from the initial drafts. Age and inferred gender are omitted from the structured references. Accent impressions are optional and carry no ranking weight.

## 5. Access and versioning

The repository includes edited questions, reference key points, turn metadata, and scoring tools. Media and verbatim transcripts are stored locally. Record source and redistribution permissions before preparing a public dataset release. Use the data to evaluate attribution within a clip or within a supplied roster. Voiceprint identification and personal attribute inference are outside the task scope.

Record affected IDs and reasons when changing question meaning, evidence intervals, reference points, or scoring rules. Report a frozen dataset version and commit hash with each result. Keep a record of fixes and retire IDs when the underlying item changes substantially.

The documentation structure follows [Datasheets for Datasets](https://arxiv.org/abs/1803.09010).
