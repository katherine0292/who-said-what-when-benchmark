# Annotation Handbook

## 1. Select clips and assign a topic

1. Assign a stable `source_id` to each original video. Record the program, episode, URL, source start and end times, media checksum, and permission status.
2. Prefer natural conversations of 3 to 10 minutes with at least two distinguishable speakers. Each clip should contain a point or question that listeners can understand in context. Sampling about one clip per 15 minutes and retaining about 30 seconds of surrounding context are starting points. Prioritize meaningful content and natural conversation boundaries.
3. Cut near a natural pause or speaker change. Verify the extracted audio duration and align its opening to the source video. Record any intro, ad, edit, added silence, or encoding discrepancy. Preserve both clocks until the source alignment is verified.
4. Assign one primary category from Science & Technology, Finance, Entertainment, Current Affairs & News, Sports, Health & Fitness, Education & Knowledge, or Lifestyle & Daily. If several categories apply, use the conversation's central question to choose one and capture additional context in a one-sentence topic. Categories are used for organization and reporting.

## 2. Round 1 | Annotate turns

| Field | Requirement | Common error |
| --- | --- | --- |
| Clip and speaker IDs | Use a stable clip ID. Assign `spk_01`, `spk_02`, and so on by first identifiable speech in the clip. Reuse the same ID when a speaker returns. | Reusing a source video ID for several clips or attributing a quotation to the person being quoted |
| Names and roles | Verify names and program roles through an audible introduction, an official program page, or another reviewed source. Record the source and verification status. Use a null value when identity is unknown. | Inferring a name or profession from voice, appearance, or a model's guess |
| Turns | Start a new turn when the speaker changes. Long contributions may be split at a meaningful boundary while retaining the same speaker ID. | Assigning a single turn to two speakers or counting applause as speech |
| Timing | Set the first sample of the local audio to 0. Use integer milliseconds and half-open intervals `[start_ms, end_ms)`. For new labels, aim to locate boundaries to the nearest 100 ms when the audio permits. | Using the source video clock or extending the last turn to cover trailing silence |
| Transcript | Keep the original spoken language and meaningful hesitations, repetitions, and negation. Mark unclear speech as `[inaudible]`. | Replacing speech with a translation or copying a host's paraphrase into the guest's turn |
| Meaning and stance | Summarize the actual claim, question, suggestion, or disagreement. Distinguish the speaker from the person they mention or quote. | Turning a question into an endorsement or presenting an interviewee's claim as verified fact |
| Voice and delivery | Describe audible timbre, prosody, relative loudness, and pace or rhythm. Use `unknown` for insufficient evidence. Accent impressions are optional. | Guessing age, ethnicity, nationality, or identity from vocal traits |

When speakers overlap, give each a separate turn with its actual boundaries. Laughter, applause, music, and silence may be logged as non-speech events. Preserve a gap for silence at the end of a clip. Flag difficult overlaps for review and exclude an item if the necessary evidence remains unintelligible. Audible laughter can support a delivery label. Visual gestures, facial expressions, and captions are outside the audio-only condition.

Choose a perceived delivery label after listening. Available labels are `neutral`, `animated`, `warm`, `encouraging`, `explanatory`, `reflective`, `concerned`, `inquiring`, `emphatic`, and `unknown`. A rising pitch during a follow-up can support `inquiring`. A discussion of failure alone gives little information about delivery. Record the audible cue and use `unknown` when cues conflict or the delivery is mixed. Calibrate annotators before scoring delivery.

## 3. Round 2 | Write questions and link evidence

1. Listen to the full clip. Write a natural question that asks who addressed a topic, what they said, and when they said it. Use a topic clue and withhold the speaker's name, key answer points, exact times, and verbatim answer. For example, ask who explained why a diner makes customers feel equal and what reason they gave. Save the detail about sharing the same counter for the reference.
2. Target one clearly identifiable speaker. If the explanation spans multiple turns, link every necessary turn. Record distinct intervals when the evidence is separated. Adjacent evidence from the same speaker can be merged. Exclude intervening speech when it contributes no evidence. If two people give equivalent answers, rewrite the question to distinguish them or exclude it as ambiguous.
3. Write one to four concise, independently assessable key points. Preserve qualifiers, negation, and causal direction. Accept equivalent paraphrases. Use a quotation when the question calls for exact wording and verify it against the audio. Record the smallest supporting interval for each point in the review log.
4. Keep the speaker ID as the main task's answer to “who.” Store verified names and roles in `identity_ref` for the roster-based track, and audible traits in `voice_ref`. Questions used to assess delivery should withhold the target delivery label.
5. Within a long turn, select the shortest complete utterance that establishes the answer. The pilot uses legacy turn boundaries with one-second resolution. Future review should refine these boundaries where the evidence occupies a shorter passage.

For example, Speaker A explains at 10–26 seconds that a situation cannot be changed. Speaker B interjects at 26–27 seconds. Speaker A adds at 27–59 seconds that a problem has a solution. A question asking for the distinction targets A and uses `[[10000, 26000], [27000, 59000]]`. A question about the first point alone uses the first interval. If B supplies part of the necessary answer, revise the item or reserve it for a track that supports multiple target speakers.

## 4. Independent review and acceptance

| Stage | Procedure | Acceptance criterion |
| --- | --- | --- |
| Calibration | Two annotators independently label a trial batch containing short exchanges, long turns, interruptions, and multiple speakers. | Reconcile differences, update the shared handbook, and retain both first drafts. |
| Review | Annotator A labels the clip and writes the item. Reviewer B answers and locates evidence independently before seeing the reference. | Both identify the same speaker, key points, and necessary evidence. Identity claims have a recorded source. |
| Adjudication | A third reviewer listens to disputed segments and records the old label, revised label, evidence, and rationale. | Exclude items with unresolved ambiguity, unintelligible evidence, or uncertain clip alignment from the gold set. |
| Release checks | Check JSON, IDs, interval bounds, checksums, leakage, grouping, and permissions. | Every gold item passes structural and human review with a retained record. |

Proposed pilot acceptance thresholds are at least 95% speaker agreement, a median temporal IoU of at least 0.80, and at least 90% agreement on key points. Freeze thresholds after calibration and report boundary errors and low-agreement cases. Use time-set IoU for multi-interval labels and report start and end errors for single intervals. For optional delivery, report Cohen's kappa, the label distribution, and the unknown rate. Defer primary scoring for labels with poor agreement. These thresholds have yet to be measured on the pilot.

Each review record should include `id`, anonymized reviewer IDs, the media hash, review status, edits to the question and key points, evidence for each point, reasons for disagreements, and the date. Model-generated drafts require independent listening review before acceptance as gold labels.
