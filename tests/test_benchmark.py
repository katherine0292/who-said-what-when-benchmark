import unittest

from wsw.common import ROOT, read_rows, timestamp_ms
from wsw.score import evaluate, temporal_iou, valid_windows
from wsw.validate import validate


class BenchmarkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = ROOT / "data"
        cls.rows = [read_rows(cls.data / f"{name}.jsonl") for name in ("inputs", "references", "clips")]

    def test_referential_integrity_and_size(self):
        summary = validate(self.data)
        self.assertEqual((summary["questions"], summary["source_videos"], summary["legacy_turns"]), (25, 5, 178))

    def test_discontinuous_evidence_penalizes_gap(self):
        ref = [[0, 48000], [136000, 190000]]
        self.assertAlmostEqual(temporal_iou([[0, 190000]], ref), 102 / 190)
        self.assertEqual(temporal_iou([[48000, 136000]], ref), 0)
        self.assertEqual(temporal_iou(ref, ref), 1)

    def test_reject_overlapping_out_of_bounds_and_non_integer_windows(self):
        for bad in ([], [[0, 15], [14, 20]], [[1, 21]], [[True, 5]], [[2, 2]], [[3, 5], [1, 2]]):
            with self.subTest(bad=bad):
                self.assertFalse(valid_windows(bad, 20))

    def test_review_rows_do_not_change_default_denominator(self):
        self.assertEqual(evaluate(*self.rows, [])["overall"]["n"], 18)
        full = evaluate(*self.rows, [], include_review=True)["overall"]
        self.assertEqual(full["n"], 25)
        self.assertEqual(full["speaker_accuracy"], 0)
        self.assertIsNone(full["joint_pass"])

    def test_human_scores_and_joint(self):
        inputs, refs, clips = self.rows
        ref = next(r for r in refs if r["id"] == "wsw_0018")
        prediction = {k: ref[k] for k in ("id", "speaker_id", "evidence_ms")}
        prediction["answer"] = "Accept the situation; find a solution to the problem."
        judgment = {"id": ref["id"], "point_scores": [1, 1], "material_contradiction": False}
        report = evaluate(inputs, refs, clips, [prediction], judgments=[judgment])
        self.assertEqual(report["overall"]["joint_pass"], round(1 / 18, 6))
        self.assertEqual(report["overall"]["meaning_credit"], 1)
        judgment["material_contradiction"] = True
        self.assertEqual(evaluate(inputs, refs, clips, [prediction], judgments=[judgment])["overall"]["joint_pass"], 0)
        judgment["point_scores"] = [1]
        with self.assertRaises(ValueError):
            evaluate(inputs, refs, clips, [prediction], judgments=[judgment])

    def test_submission_ids(self):
        for bad in ([{"id": "unknown"}], [{"id": "wsw_0018"}] * 2):
            with self.assertRaises(ValueError):
                evaluate(*self.rows, bad)

    def test_clock_normalization(self):
        self.assertEqual(timestamp_ms("00:01:03:38"), 3818000)
        with self.assertRaises(ValueError):
            timestamp_ms("00:01:80")


if __name__ == "__main__":
    unittest.main()
