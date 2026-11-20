"""Tests for score_candidates, scoring_rules, scoring_core and evaluate. Offline, with tiny made up fixtures."""
import contextlib
import copy
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hiring_fixtures as fx  # noqa: F401  (sets sys.path)
import evaluate
import hlib
import jev
import mock_jev
import scoring_rules
import score_candidates as sc

SAMPLE = fx.ROOT / "data" / "sample"


def run_main(argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = sc.main(argv)
    return code, out.getvalue()


class RulesEngineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.card = fx.scorecard()
        cls.records, _ = sc.run_scoring(cls.card, fx.make_candidates(), "rules")
        cls.by_id = {r["candidate_id"]: r for r in cls.records}

    def test_tiers_for_clear_cases(self):
        self.assertEqual(self.by_id["T001"]["tier"], "strong")
        self.assertEqual(self.by_id["T002"]["tier"], "maybe")
        self.assertEqual(self.by_id["T003"]["tier"], "below")

    def test_keyword_stuffing_does_not_pass(self):
        record = self.by_id["T004"]
        self.assertNotIn(record["tier"], ("strong", "maybe"))
        self.assertTrue(all(v["level"] <= 1 for v in record["criteria"].values()))

    def test_injection_forces_review_and_is_ignored(self):
        record = self.by_id["T005"]
        self.assertEqual(record["tier"], "review")
        self.assertIn("prompt_injection_suspected", record["flags"])
        self.assertTrue(record["needs_human"])
        self.assertLess(record["weighted_score"], 75)

    def test_thin_text_goes_to_a_person(self):
        record = self.by_id["T006"]
        self.assertIn("low_confidence", record["flags"])
        self.assertEqual(record["tier"], "review")

    def test_score_maths_matches_spec(self):
        for record in self.records:
            levels = {k: v["level"] for k, v in record["criteria"].items()}
            expected = round(sum(c["weight"] * levels[c["id"]] / 4.0 for c in self.card["criteria"]), 1)
            self.assertEqual(record["weighted_score"], expected)
            self.assertIn(record["tier"], hlib.TIERS)
            self.assertEqual(record["engine"], "rules")

    def test_record_shape(self):
        record = self.by_id["T001"]
        for key in ("candidate_id", "role_id", "engine", "criteria", "gates", "deal_breakers", "weighted_score",
                    "tier", "needs_human", "reasons", "flags"):
            self.assertIn(key, record)
        for item in record["criteria"].values():
            self.assertTrue(0 <= item["level"] <= 4)
            self.assertTrue(0.0 <= item["confidence"] <= 1.0)
        self.assertEqual(record["gates"], {"work_authorization": "yes"})
        self.assertTrue(record["reasons"])

    def test_never_writes_rejected(self):
        self.assertNotIn("rejected", json.dumps(self.records).lower())

    def test_name_and_pronouns_do_not_change_the_score(self):
        base = fx.make_candidates()[0]
        other = copy.deepcopy(base)
        other["name"] = "Arjun Rao"
        other["email"] = "arjun.rao@example.org"
        other["resume_text"] = "Mr. Arjun Rao, he/him. " + base["resume_text"].replace("I ", "He ", 1)
        a, _ = sc.run_scoring(self.card, [base], "rules")
        b, _ = sc.run_scoring(self.card, [other], "rules")
        self.assertEqual(a[0]["weighted_score"], b[0]["weighted_score"])
        self.assertEqual(a[0]["tier"], b[0]["tier"])

    def test_evidence_is_a_quote_from_the_text(self):
        evidence = self.by_id["T001"]["criteria"]["ticket_handling"]["evidence"]
        self.assertTrue(evidence)
        self.assertIn(evidence.rstrip(".").split("...")[0][:30].lower(), fx.STRONG.lower().replace("\n", " "))

    def test_gate_no_is_below_and_needs_a_person(self):
        candidate = fx.make_candidates()[0]
        candidate["answers"] = {"work_authorization": "no"}
        record = sc.run_scoring(self.card, [candidate], "rules")[0][0]
        self.assertEqual(record["tier"], "below")
        self.assertTrue(record["needs_human"])
        self.assertTrue(any("person confirms" in r.lower() for r in record["reasons"]))

    def test_unknown_hard_gate_is_flagged_and_reviewed(self):
        candidate = fx.make_candidates()[0]
        candidate["answers"] = {}
        record = sc.run_scoring(self.card, [candidate], "rules")[0][0]
        self.assertEqual(record["gates"]["work_authorization"], "unknown")
        self.assertIn("gate_unknown", record["flags"])
        self.assertEqual(record["tier"], "review")
        self.assertTrue(record["needs_human"])

    def test_unknown_soft_gate_needs_a_person_but_keeps_tier(self):
        card = fx.scorecard()
        card["gates"][0]["kind"] = "soft"
        candidate = fx.make_candidates()[0]
        candidate["answers"] = {}
        record = sc.run_scoring(card, [candidate], "rules")[0][0]
        self.assertIn("gate_unknown", record["flags"])
        self.assertEqual(record["tier"], "strong")
        self.assertTrue(record["needs_human"])

    def test_deal_breaker_yes_is_below(self):
        candidate = fx.make_candidates()[0]
        candidate["answers"] = {"work_authorization": "yes", "no_weekends": "yes"}
        record = sc.run_scoring(self.card, [candidate], "rules")[0][0]
        self.assertEqual(record["tier"], "below")
        self.assertTrue(record["needs_human"])

    def test_gate_found_in_a_sentence(self):
        gate = {"id": "work_authorization", "question": "?", "kind": "hard"}
        self.assertEqual(scoring_rules.resolve_gate(gate, {}, "I am authorized to work in the country."), "yes")
        self.assertEqual(scoring_rules.resolve_gate(gate, {}, "I am not authorized to work here."), "no")
        self.assertEqual(scoring_rules.resolve_gate(gate, {}, "I like cooking."), "unknown")

    def test_strong_with_low_confidence_needs_a_person(self):
        levels = {c["id"]: {"level": 4, "confidence": 0.7, "evidence": "x"} for c in self.card["criteria"]}
        record = sc.finish_record(self.card, {"candidate_id": "X"}, "import", levels,
                                  {"work_authorization": "yes"}, {"no_weekends": "no"}, False)
        self.assertEqual(record["tier"], "strong")
        self.assertTrue(record["needs_human"])

    def test_find_evidence_prefers_real_sentences(self):
        text = "Skills: tickets, zendesk, helpdesk, queue, support, resolved\nI resolved tickets for two years."
        self.assertEqual(scoring_rules.find_evidence(text, ["tickets", "zendesk"]), "I resolved tickets for two years.")
        self.assertEqual(scoring_rules.find_evidence("nothing here", ["tickets"]), "")


class CommandTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        hlib.save_json(self.dir / "card.json", fx.scorecard())
        with open(self.dir / "c.jsonl", "w", encoding="utf-8") as handle:
            for row in fx.make_candidates():
                handle.write(json.dumps(row) + "\n")
            other = dict(fx.make_candidates()[0], candidate_id="OTHER", role_id="another-role")
            handle.write(json.dumps(other) + "\n")

    def tearDown(self):
        self.tmp.cleanup()

    def args(self, *extra):
        return ["run", "--scorecard", str(self.dir / "card.json"), "--candidates", str(self.dir / "c.jsonl"),
                "--out", str(self.dir / "scores.json")] + list(extra)

    def test_run_rules_writes_files_and_filters_by_role(self):
        code, text = run_main(self.args("--engine", "rules"))
        self.assertEqual(code, 0)
        scores = hlib.load_json(self.dir / "scores.json")
        self.assertEqual(sorted(r["candidate_id"] for r in scores), ["T001", "T002", "T003", "T004", "T005", "T006"])
        rows = hlib.read_csv(self.dir / "shortlist.csv")
        self.assertEqual(list(rows[0].keys()), hlib.SHORTLIST_COLUMNS)
        self.assertEqual([r["rank"] for r in rows], [str(i) for i in range(1, len(rows) + 1)])
        self.assertTrue(all(r["tier"] in ("strong", "maybe", "review") for r in rows))
        self.assertEqual(rows[0]["candidate_id"], "T001")
        self.assertIn("A person decides", text)

    def test_run_mock_engine_same_code_path(self):
        code, text = run_main(self.args("--engine", "mock"))
        self.assertEqual(code, 0)
        self.assertIn("FAKE Jev for practice", text)
        scores = {r["candidate_id"]: r for r in hlib.load_json(self.dir / "scores.json")}
        self.assertEqual({r["engine"] for r in scores.values()}, {"mock"})
        self.assertGreater(scores["T001"]["weighted_score"], scores["T003"]["weighted_score"])
        for record in scores.values():
            self.assertIn(record["tier"], hlib.TIERS)
            self.assertNotIn("rejected", json.dumps(record).lower())
        self.assertIn("prompt_injection_suspected", scores["T005"]["flags"])
        self.assertEqual(scores["T005"]["tier"], "review")

    def test_mock_requests_hold_no_personal_details(self):
        seen = []
        original = jev.JevClient.ask

        def spy(client, state, questions):
            seen.append(state)
            return original(client, state, questions)

        with mock.patch.object(jev.JevClient, "ask", spy):
            run_main(self.args("--engine", "mock"))
        joined = "\n".join(seen)
        for secret in ("example.com", "555-0101", "Maya", "Stone", "https://"):
            self.assertNotIn(secret, joined)
        self.assertNotIn("Ignore all previous", joined)

    def test_jev_without_key_is_a_plain_message(self):
        with mock.patch.dict(os.environ, {}, clear=True), mock.patch.object(hlib, "load_env_file", lambda *a, **k: None):
            code, text = run_main(self.args("--engine", "jev"))
        self.assertEqual(code, 1)
        self.assertIn("docs/JEV-OPTIONAL.md", text)

    def test_jev_dry_run_needs_no_key_and_sends_nothing(self):
        with mock.patch.dict(os.environ, {}, clear=True), mock.patch.object(jev.JevClient, "ask", side_effect=AssertionError):
            code, text = run_main(self.args("--engine", "jev", "--dry-run"))
        self.assertEqual(code, 0)
        self.assertIn("Nothing sent", text)

    def test_packet_is_redacted_and_flags_injection(self):
        code, _ = run_main(["packet", "--scorecard", str(self.dir / "card.json"), "--candidates", str(self.dir / "c.jsonl"),
                            "--out", str(self.dir / "packet.json")])
        self.assertEqual(code, 0)
        packet = hlib.load_json(self.dir / "packet.json")
        blob = json.dumps(packet)
        for secret in ("example.com", "555-0101", "Maya Stone"):
            self.assertNotIn(secret, blob)
        flags = {c["candidate_id"]: c["injection_suspected"] for c in packet["candidates"]}
        self.assertTrue(flags["T005"])
        self.assertFalse(flags["T001"])
        self.assertEqual(len(packet["candidates"]), 6)

    def test_import_computes_tiers_and_notes_gaps(self):
        crit = {c["id"]: {"level": 4, "confidence": 0.9, "evidence": "q"} for c in fx.SCORECARD["criteria"]}
        weak = {"ticket_handling": {"level": 1, "confidence": 0.9, "evidence": "q"}}
        entries = [{"candidate_id": "A", "criteria": crit, "gates": {"work_authorization": "yes"}},
                   {"candidate_id": "B", "criteria": weak, "gates": {"work_authorization": "yes"}},
                   {"candidate_id": "C", "criteria": crit, "gates": {"work_authorization": "yes"},
                    "flags": ["prompt_injection_suspected"]}]
        hlib.save_json(self.dir / "claude.json", entries)
        code, text = run_main(["import", "--scorecard", str(self.dir / "card.json"), "--scores", str(self.dir / "claude.json"),
                               "--out", str(self.dir / "imp.json")])
        self.assertEqual(code, 0)
        got = {r["candidate_id"]: r for r in hlib.load_json(self.dir / "imp.json")}
        self.assertEqual(got["A"]["tier"], "strong")
        self.assertEqual(got["A"]["weighted_score"], 100.0)
        self.assertEqual(got["B"]["tier"], "review")
        self.assertEqual(got["C"]["tier"], "review")
        self.assertEqual(got["A"]["engine"], "import")
        self.assertIn("had no level", text)

    def test_report_prints_counts_and_top_rows(self):
        run_main(self.args("--engine", "rules"))
        code, text = run_main(["report", "--scores", str(self.dir / "scores.json")])
        self.assertEqual(code, 0)
        self.assertIn("6 scored", text)
        self.assertIn("T001", text)
        self.assertIn("need a person", text)

    def test_missing_files_give_a_plain_message(self):
        code, text = run_main(["run", "--scorecard", str(self.dir / "nope.json"), "--candidates", str(self.dir / "c.jsonl")])
        self.assertEqual(code, 1)
        self.assertIn("Could not read", text)


class EvaluateTests(unittest.TestCase):
    def test_agreement_traps_and_dangerous_misses(self):
        scores = [{"candidate_id": "A", "tier": "strong", "weighted_score": 90},
                  {"candidate_id": "B", "tier": "below", "weighted_score": 10},
                  {"candidate_id": "C", "tier": "maybe", "weighted_score": 60},
                  {"candidate_id": "D", "tier": "below", "weighted_score": 20}]
        key = {"version": 1, "candidates": {
            "A": {"expected_tier": "strong", "traps": []},
            "B": {"expected_tier": "strong", "traps": ["non_traditional"], "why": "Real experience."},
            "C": {"expected_tier": "strong", "traps": [], "also_acceptable": ["maybe"]},
            "D": {"expected_tier": "review", "traps": ["prompt_injection"]},
            "E": {"expected_tier": "maybe", "traps": []}}}
        result = evaluate.evaluate(scores, key)
        self.assertEqual(result["total"], 4)
        self.assertEqual(result["exact"], 1)
        self.assertEqual(result["ok"], 2)
        self.assertEqual(sorted(r["id"] for r in result["dangerous"]), ["B", "D"])
        self.assertEqual(result["missing"], ["E"])
        self.assertEqual(result["traps"]["non_traditional"], {"n": 1, "ok": 0})
        text = evaluate.format_report(result)
        self.assertIn("Dangerous misses: 2", text)
        self.assertIn("Confusion", text)

    def test_cli_and_fail_under(self):
        with tempfile.TemporaryDirectory() as tmp:
            hlib.save_json(Path(tmp) / "s.json", [{"candidate_id": "A", "tier": "below", "weighted_score": 1}])
            hlib.save_json(Path(tmp) / "k.json", {"candidates": {"A": {"expected_tier": "strong", "traps": []}}})
            base = ["--scores", str(Path(tmp) / "s.json"), "--key", str(Path(tmp) / "k.json")]
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(evaluate.main(base), 0)
                self.assertEqual(evaluate.main(base + ["--fail-under", "0.5"]), 1)


class SampleDataTests(unittest.TestCase):
    def test_pipeline_on_sample_data_if_present(self):
        key_path = SAMPLE / "answer_key.json"
        cands = SAMPLE / "candidates.jsonl"
        cards = sorted(SAMPLE.glob("scorecard-*.json"))
        if not (key_path.exists() and cands.exists() and cards):
            self.skipTest("data/sample is not there yet")
        key = hlib.load_json(key_path)
        rows = hlib.read_candidates(cands)
        records = []
        for path in cards:
            card = hlib.load_json(path)
            mine = [r for r in rows if r.get("role_id") == card["role_id"]]
            part, _ = sc.run_scoring(card, mine, "rules")
            records += part
        self.assertEqual(len(records), len(rows))
        self.assertNotIn("rejected", json.dumps(records).lower())
        result = evaluate.evaluate(records, key)
        self.assertEqual(result["missing"], [])
        injected = [r for r in result["rows"] if "prompt_injection" in r["traps"]]
        self.assertTrue(injected)
        for row in injected:
            self.assertEqual(row["got"], "review", "%s: injection not sent to review" % row["id"])


if __name__ == "__main__":
    unittest.main()
