"""Tests for funnel_calculator.py, budget_planner.py and pipeline.py (no network, no other tools needed)."""
import datetime as dt
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hiring_fixtures import TempDir, run_main  # noqa: E402

import budget_planner  # noqa: E402
import funnel_calculator as fc  # noqa: E402
import pipeline as pl  # noqa: E402
from hlib import PIPELINE_COLUMNS, STAGES, write_csv  # noqa: E402


class FunnelTests(unittest.TestCase):
    def test_one_hire_works_backwards_with_default_assumptions(self):
        result = fc.plan(1, fc.STARTING_ASSUMPTIONS)
        self.assertEqual(result["offers"], 2)
        self.assertEqual(result["finalists"], 4)
        self.assertEqual(result["interviews"], 10)
        self.assertEqual(result["shortlisted"], 15)
        self.assertEqual(result["screened"], 30)
        self.assertEqual(result["applicants"], 50)
        self.assertEqual(result["prospects_to_contact"], 500)

    def test_batch_hiring_plans_extra_offers_and_backups(self):
        result = fc.plan(5, fc.STARTING_ASSUMPTIONS)
        self.assertEqual(result["offers"], 7)
        self.assertEqual(result["overhire_offers"], 2)
        self.assertEqual(result["backup_list"], 3)

    def test_output_prints_the_assumptions_labelled(self):
        code, out, _ = run_main(fc, ["--hires", "2"])
        self.assertEqual(code, 0)
        self.assertIn("STARTING ASSUMPTIONS", out)
        self.assertIn("offer_acceptance", out)
        self.assertIn("not benchmarks", out)

    def test_weeks_and_weekly_applicants(self):
        code, out, _ = run_main(fc, ["--hires", "1", "--weeks", "5", "--weekly-applicants", "10", "--json"])
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertEqual(data["timeline"]["applicants_needed_per_week"], 10)
        self.assertEqual(data["timeline"]["weeks_to_collect_applicants"], 5)
        self.assertEqual(data["timeline"]["weeks_to_fill"], 5 + 4 + 2)

    def test_assumptions_file_overrides_and_unknown_key_fails(self):
        with TempDir() as tmp:
            good = tmp / "good.json"
            good.write_text(json.dumps({"offer_acceptance": 0.5}), encoding="utf-8")
            code, out, _ = run_main(fc, ["--hires", "1", "--assumptions", str(good), "--json"])
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(out)["plan"]["offers"], 2)
            self.assertEqual(json.loads(out)["plan"]["offers"], fc.plan(1, dict(fc.STARTING_ASSUMPTIONS, offer_acceptance=0.5))["offers"])
            bad = tmp / "bad.json"
            bad.write_text(json.dumps({"made_up_rate": 0.5}), encoding="utf-8")
            code, out, _ = run_main(fc, ["--hires", "1", "--assumptions", str(bad)])
            self.assertEqual(code, 1)
            self.assertIn("Unknown assumption", out)

    def test_rate_out_of_range_and_zero_hires_fail(self):
        with TempDir() as tmp:
            bad = tmp / "bad.json"
            bad.write_text(json.dumps({"offer_acceptance": 0}), encoding="utf-8")
            self.assertEqual(run_main(fc, ["--hires", "1", "--assumptions", str(bad)])[0], 1)
        self.assertEqual(run_main(fc, ["--hires", "0"])[0], 1)

    def test_actual_rates_replace_assumptions_only_with_five_people(self):
        rows = [{"candidate_id": "C%d" % i, "stage": "applied", "notes": ""} for i in range(6)]
        rows += [{"candidate_id": "S%d" % i, "stage": "screened", "notes": ""} for i in range(4)]
        observed = fc.observed_rates(rows)
        self.assertIn("applicant_to_screened", observed)
        self.assertAlmostEqual(observed["applicant_to_screened"]["rate"], 0.4)
        self.assertNotIn("screened_to_shortlist", observed)  # only 4 reached screened
        with TempDir() as tmp:
            path = tmp / "pipeline.csv"
            write_csv(path, PIPELINE_COLUMNS, rows)
            code, out, _ = run_main(fc, ["--hires", "1", "--actual", str(path), "--json"])
            self.assertEqual(code, 0)
            data = json.loads(out)
            self.assertAlmostEqual(data["assumptions"]["applicant_to_screened"], 0.4)
            self.assertIn("observed", data["assumption_sources"]["applicant_to_screened"])
            self.assertEqual(data["assumption_sources"]["screened_to_shortlist"], "starting assumption")


class BudgetTests(unittest.TestCase):
    def cfg(self, **extra):
        cfg = dict(budget_planner.DEFAULTS)
        cfg.update({"board_spend": 0.0, "tool_spend": 0.0, "budget": None, "hourly_value": 30.0})
        cfg.update(extra)
        return cfg

    def test_loaded_cost_uses_employer_cost_percent(self):
        result = budget_planner.build(60000, 2, self.cfg(employer_cost_pct=25.0))
        self.assertEqual(result["loaded_yearly_cost_per_employee"], 75000)
        self.assertEqual(result["loaded_yearly_cost_all_hires"], 150000)

    def test_tiers_follow_ratio_to_one_month_of_pay(self):
        tiers = {b: budget_planner.tier_for_budget(b, 60000)[0] for b in (0, 100, 1000, 2000, 5000, 20000)}
        self.assertEqual(tiers, {0: "none", 100: "none", 1000: "small", 2000: "medium", 5000: "large", 20000: "large"})

    def test_recruiter_path_uses_fee_percent_of_base_pay(self):
        paths = budget_planner.path_costs(60000, 1, self.cfg(recruiter_fee_pct=20.0))
        self.assertGreaterEqual(paths["recruiter"]["cost"], 12000)
        self.assertLess(paths["self_with_system"]["cost"], paths["recruiter"]["cost"])
        self.assertGreater(paths["boards_plus_system"]["cost"], 0)

    def test_budget_coverage_flags(self):
        result = budget_planner.build(60000, 1, self.cfg(budget=1000.0))
        self.assertTrue(result["paths"]["self_with_system"]["covered_by_budget"])
        self.assertFalse(result["paths"]["recruiter"]["covered_by_budget"])
        self.assertIn("tier", result)
        self.assertNotIn("tier", budget_planner.build(60000, 1, self.cfg()))

    def test_cli_prints_assumptions_currency_and_recommendation(self):
        code, out, _ = run_main(budget_planner, ["--base-pay", "60000", "--hires", "2", "--budget", "4000", "--currency", "eur"])
        self.assertEqual(code, 0)
        self.assertIn("EUR", out)
        self.assertIn("ASSUMPTIONS", out)
        self.assertIn("Recommendation", out)
        self.assertIn("Not financial advice", out)

    def test_cli_json_and_bad_input(self):
        code, out, _ = run_main(budget_planner, ["--base-pay", "50000", "--hires", "1", "--json"])
        self.assertEqual(code, 0)
        self.assertIn("paths", json.loads(out))
        self.assertEqual(run_main(budget_planner, ["--base-pay", "0", "--hires", "1"])[0], 1)
        self.assertEqual(run_main(budget_planner, ["--base-pay", "5", "--hires", "1", "--board-spend", "-3"])[0], 1)
        self.assertEqual(run_main(budget_planner, ["--hires", "1"])[0], 2)


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self._tmp = TempDir()
        self.tmp = self._tmp.__enter__()
        self.base = str(self.tmp / "hiring")
        self.args = ["--role", "r1", "--base", self.base]
        run_main(pl, ["init", "r1", "--base", self.base])

    def tearDown(self):
        self._tmp.__exit__()

    def rows(self):
        from hlib import read_csv
        return read_csv(self.tmp / "hiring" / "r1" / "pipeline.csv")

    def add(self, name, stage="applied"):
        return run_main(pl, ["add"] + self.args + ["--name", name, "--stage", stage])

    def test_init_creates_header_and_is_safe_to_repeat(self):
        path = self.tmp / "hiring" / "r1" / "pipeline.csv"
        self.assertEqual(path.read_text(encoding="utf-8").strip(), ",".join(PIPELINE_COLUMNS))
        code, out, _ = run_main(pl, ["init", "r1", "--base", self.base])
        self.assertEqual(code, 0)
        self.assertIn("Already there", out)

    def test_add_assigns_ids_and_rejects_unknown_stage(self):
        self.assertEqual(self.add("Ada Example")[0], 0)
        self.add("Bo Example")
        self.assertEqual([r["candidate_id"] for r in self.rows()], ["C001", "C002"])
        code, out, _ = self.add("Cy", stage="flying")
        self.assertEqual(code, 1)
        self.assertIn("Unknown stage", out)

    def test_move_stamps_date_and_validates(self):
        self.add("Ada")
        code, _, _ = run_main(pl, ["move"] + self.args + ["C001", "screened", "--date", "2026-12-01"])
        self.assertEqual(code, 0)
        self.assertEqual(self.rows()[0]["stage"], "screened")
        self.assertEqual(self.rows()[0]["stage_changed_on"], "2026-12-01")
        self.assertEqual(run_main(pl, ["move"] + self.args + ["C001", "nowhere"])[0], 1)
        self.assertEqual(run_main(pl, ["move"] + self.args + ["C999", "screened"])[0], 1)
        self.assertEqual(run_main(pl, ["move"] + self.args + ["C001", "applied"])[0], 1)  # backwards
        self.assertEqual(run_main(pl, ["move"] + self.args + ["C001", "applied", "--force"])[0], 0)

    def test_rejection_needs_a_human_yes_and_keeps_last_active(self):
        self.add("Ada", stage="shortlisted")
        code, out, _ = run_main(pl, ["move"] + self.args + ["C001", "rejected"])
        self.assertEqual(code, 1)
        self.assertIn("human decision", out)
        self.assertEqual(run_main(pl, ["move"] + self.args + ["C001", "rejected", "--confirmed"])[0], 0)
        self.assertIn("last_active:shortlisted", self.rows()[0]["notes"])
        self.assertEqual(pl.effective_stage(self.rows()[0]), "shortlisted")
        code, out, _ = run_main(pl, ["move"] + self.args + ["C001", "applied"])
        self.assertEqual(code, 1)
        self.assertIn("closed", out)

    def test_accepted_can_become_hired(self):
        self.add("Ada", stage="accepted")
        self.assertEqual(run_main(pl, ["move"] + self.args + ["C001", "hired"])[0], 0)

    def test_conversion_counts_people_who_moved_on(self):
        rows = [{"candidate_id": "A", "stage": "interviewed", "notes": ""},
                {"candidate_id": "B", "stage": "rejected", "notes": "last_active:screened"},
                {"candidate_id": "C", "stage": "applied", "notes": ""},
                {"candidate_id": "D", "stage": "declined", "notes": ""}]
        reached = pl.reached_counts(rows)
        self.assertEqual(reached["applied"], 4)
        self.assertEqual(reached["screened"], 3)
        self.assertEqual(reached["offer"], 1)
        self.assertEqual(reached["accepted"], 0)
        first = pl.conversions(rows)[1]
        self.assertEqual((first["from"], first["to"], first["n_from"], first["n_to"]), ("applied", "screened", 4, 3))

    def test_stale_rows_and_median_days(self):
        today = dt.date(2026, 12, 20)
        rows = [{"candidate_id": "A", "name": "A", "stage": "screened", "stage_changed_on": "2026-12-01"},
                {"candidate_id": "B", "name": "B", "stage": "screened", "stage_changed_on": "2026-12-17"},
                {"candidate_id": "C", "name": "C", "stage": "hired", "stage_changed_on": "2026-01-01"}]
        stale = pl.stale_rows(rows, today)
        self.assertEqual([r["candidate_id"] for r, _ in stale], ["A"])
        self.assertEqual(pl.median_days_by_stage(rows, today)["screened"], 11)

    def test_stats_command_output(self):
        self.add("Ada")
        self.add("Bo", stage="screened")
        code, out, _ = run_main(pl, ["stats"] + self.args)
        self.assertEqual(code, 0)
        self.assertIn("Candidates: 2", out)
        self.assertIn("Conversion between consecutive stages", out)

    def test_weekly_report_names_one_action_per_stuck_person_and_advice(self):
        with open(self.tmp / "hiring" / "r1" / "pipeline.csv", "w", encoding="utf-8", newline="") as handle:
            pass
        rows = [{"candidate_id": "C%03d" % i, "name": "P%d" % i, "stage": "applied" if i < 6 else "screened",
                 "stage_changed_on": "2026-11-01", "next_action": "", "next_action_due": "", "notes": ""} for i in range(1, 8)]
        rows[0]["next_action"] = "Call Ada"
        rows[0]["next_action_due"] = "2026-12-01"
        write_csv(self.tmp / "hiring" / "r1" / "pipeline.csv", PIPELINE_COLUMNS, rows)
        out_file = self.tmp / "WEEKLY.md"
        code, _, _ = run_main(pl, ["weekly"] + self.args + ["--out", str(out_file), "--today", "2026-12-20"])
        self.assertEqual(code, 0)
        text = out_file.read_text(encoding="utf-8")
        self.assertIn("Call Ada (due 2026-12-01)", text)
        self.assertIn("Screen against the scorecard", text)
        self.assertIn("What to change:", text)
        self.assertNotIn("\u2014", text)
        self.assertNotIn("\u2013", text)

    def test_weekly_with_too_little_data_says_so(self):
        self.add("Ada")
        out_file = self.tmp / "W.md"
        run_main(pl, ["weekly"] + self.args + ["--out", str(out_file)])
        self.assertIn("Not enough data yet", out_file.read_text(encoding="utf-8"))

    def test_missing_pipeline_file_is_a_friendly_error(self):
        code, out, _ = run_main(pl, ["stats", "--role", "nope", "--base", self.base])
        self.assertEqual(code, 1)
        self.assertIn("init", out)

    def test_all_stages_known(self):
        for stage in STAGES:
            self.assertIn(stage, pl.STAGE_INDEX)


if __name__ == "__main__":
    unittest.main()
