# Migration Audit and Audio Review Queue

## Changes to the source annotations

- Thirteen per-clip Round 1 JSON files used an invalid closing quotation mark in `video_id`. The aggregate file repeats those same 13 records. The converter repairs that field and preserves other source wording in the local archive.
- Pair annotations by clip directory and use aggregate files for comparison. This resolves the legacy clip references `case_001` for `wsw_0001` and `v4` for `wsw_0012`. The audit keeps a mapping from every legacy question ID to its zero-padded ID.
- Normalize the four-part source clock `00:01:03:38` for `v5-8` to `01:03:38` by removing the extra leading zero component. Turn timing still requires review.
- In `v3-3`, one turn is missing `end_time` and uses a timestamp as a key. Another uses 80 in the seconds field. Both endpoints are stored as `null` with `invalid_legacy_clock`. The original values are available in the local archive.
- The migration rewrites questions to reduce answer leakage and derives key points from the source turns and answers. Published topic and role metadata use English translations. Item-level turn edits and differences between the per-clip and aggregate files appear in `data/migration_audit.jsonl`. Independent audio review is pending.

| Item | Text-based evidence edit |
| --- | --- |
| `wsw_0003` | Turn 4 sets up the school visit. Turn 6 contains the audition and age confirmation. Keep both intervals. |
| `wsw_0014` | The per-clip records support `[0, 48000)` and `[136000, 190000)`. Record the aggregate's omission of the second turn. |
| `wsw_0018` | Turn 2 explains a situation and turn 4 explains a problem. The intervening acknowledgment belongs to another speaker. |
| `wsw_0020` | Turns 2 and 3 cover the reason for waiting and the alternative. Merge the adjacent evidence intervals. |
| `wsw_0024` | Turn 2 critiques authenticity. Add turns 4 and 8 for the proposed alternative and practice method. Keep the item in the audio review queue. |

## Seven items for priority audio review

| Item and clip | Discrepancy | Review action |
| --- | --- | --- |
| `wsw_0001`, v1-1 | Reported window 252 s, local MP3 254.145 s | Align the opening and end. Check for an extra intro or different edit. |
| `wsw_0002`, v1-2 | Reported window 323 s, local MP3 298.083 s | Locate the first and last utterances in the source to determine which boundary or export differs. |
| `wsw_0009`, v3-2 | Same reported source window as v3-3, with different audio and video bytes | Verify both clip boundaries and keep the clips together in any split until resolved. |
| `wsw_0010`, v3-3 | Shared reported window, 180.010 s of audio versus 193 s reported, and two invalid turn clocks | Rebuild the fourth and sixth turn boundaries and verify the target turn against the local edit. |
| `wsw_0015`, v4-3 | Turns extend to 239 s, local MP3 221.022 s | Listen from 3:20 onward and match the correct export or relabel the final turns. |
| `wsw_0017`, v5-1 | Reported window 229 s, local MP3 239.020 s | Check opening and ending offsets and verify the target evidence. |
| `wsw_0024`, v5-8 | Turns extend to 264 s, local MP3 222.015 s, with conflicting aggregate and per-clip answers | Match the source edit and verify all three key points and their intervals. |

The default scorer uses the 18 `text_aligned` items. Pass `--include-review` to run all 25 as a workflow check. All items still require independent listening review. In v2-3, for example, the second turn begins with a continuation of the prior sentence and a question. Verify the speaker change and trim the evidence to the guest's explanation. MP3 durations above are tool estimates.
