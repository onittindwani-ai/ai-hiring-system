"""Tests for the sample data in data/sample (company, scorecards, 60 candidates, answer key).

Run from the repo root:
    python3 -m unittest tests.test_sample_data

Uses only the standard library. Does not import any tool.
"""
import json
import re
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SAMPLE = ROOT / "data" / "sample"

ROLES = ["sales-development-rep", "bookkeeper", "backend-engineer"]
SOURCES = {"form", "email", "board_export", "sourced", "referral"}
TIERS = {"strong", "maybe", "below", "review"}
TRAPS = {"keyword_stuffing", "career_gap", "non_traditional", "overqualified", "title_inflation",
         "prompt_injection", "non_native_english", "name_origin_neutral", "thin_resume", "long_resume"}
CANDIDATE_FIELDS = ["candidate_id", "role_id", "source", "name", "email", "phone", "location", "links",
                    "resume_text", "answers"]
EM, EN = chr(0x2014), chr(0x2013)

# Terms that must never appear as scorecard criteria text (protected traits and proxies).
BANNED_PATTERNS = [r"\bage\b", r"\bgender\b", r"\brace\b", r"\breligion\b", r"\bnationality\b", r"\bmarital\b",
                   r"\bfamily status\b", r"\bdisability\b", r"\bphoto\b", r"\baccent\b", r"\bculture fit\b",
                   r"\bnative speaker\b", r"\bdigital native\b", r"\byoung\b", r"\bmarried\b", r"\bpregnan"]


def load_json(name):
    with open(SAMPLE / name, encoding="utf-8") as handle:
        return json.load(handle)


def load_candidates():
    rows = []
    with open(SAMPLE / "candidates.jsonl", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def scorecard_problems(card):
    """Local copy of the scorecard rules from the build contract. Returns a list of problems."""
    problems = []
    criteria = card.get("criteria", [])
    if not 5 <= len(criteria) <= 8:
        problems.append("need 5 to 8 criteria, got %d" % len(criteria))
    if sum(c.get("weight", 0) for c in criteria) != 100:
        problems.append("weights do not sum to 100")
    if sum(1 for c in criteria if c.get("type") == "must") < 3:
        problems.append("need at least 3 must criteria")
    ids = set()
    for c in criteria:
        cid = c.get("id")
        ids.add(cid)
        if not isinstance(c.get("weight"), int) or not 5 <= c["weight"] <= 30:
            problems.append("%s: weight must be an integer 5 to 30" % cid)
        if c.get("type") not in ("must", "nice"):
            problems.append("%s: type must be must or nice" % cid)
        if c.get("type") == "must" and c.get("min_level") not in (1, 2, 3):
            problems.append("%s: must needs min_level 1 to 3" % cid)
        levels = c.get("levels", [])
        if len(levels) != 5 or any(not str(lv).startswith("%d " % i) for i, lv in enumerate(levels)):
            problems.append("%s: levels must be 5 strings starting 0 to 4" % cid)
        kws = c.get("keywords", [])
        if not 4 <= len(kws) <= 12:
            problems.append("%s: keywords must be 4 to 12" % cid)
        if any(k != k.lower() for k in kws):
            problems.append("%s: keywords must be lowercase" % cid)
        for field in ("name", "what_good_looks_like", "evidence_needed", "jev_question"):
            if not c.get(field):
                problems.append("%s: missing %s" % (cid, field))
    for q in card.get("interview_questions", []):
        if q.get("criterion_id") not in ids:
            problems.append("interview question points at unknown criterion %s" % q.get("criterion_id"))
    for key in ("role_id", "title", "level", "mission", "outcomes_90_days", "gates", "deal_breakers", "work_sample",
                "red_flags", "sourcing_channels", "pay_research_hint", "automation_note"):
        if key not in card:
            problems.append("missing key %s" % key)
    flat = json.dumps(card).lower()
    for pattern in BANNED_PATTERNS:
        if re.search(pattern, flat):
            problems.append("banned term matches %s" % pattern)
    return problems


class SampleDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.company = load_json("company.json")
        cls.cards = {r: load_json("scorecard-%s.json" % r) for r in ROLES}
        cls.cands = load_candidates()
        cls.key = load_json("answer_key.json")["candidates"]

    # company and scorecards
    def test_company_is_fictional(self):
        self.assertEqual(self.company["name"], "Northlight Home Services")
        self.assertTrue(self.company["fictional"])
        self.assertEqual(self.company["size"]["people"], 14)
        self.assertEqual(len(self.company["size"]["cities"]), 2)
        self.assertEqual({r["role_id"] for r in self.company["open_roles"]}, set(ROLES))

    def test_scorecards_pass_structure_check(self):
        for role, card in self.cards.items():
            self.assertEqual(card["role_id"], role)
            self.assertEqual(scorecard_problems(card), [], role)

    def test_scorecards_are_distinct(self):
        titles = {c["title"] for c in self.cards.values()}
        self.assertEqual(len(titles), 3)

    # candidates
    def test_sixty_ids_unique_and_in_order(self):
        ids = [c["candidate_id"] for c in self.cands]
        self.assertEqual(ids, ["C%03d" % i for i in range(1, 61)])
        self.assertEqual(len(set(ids)), 60)

    def test_twenty_per_role_in_blocks(self):
        counts = Counter(c["role_id"] for c in self.cands)
        self.assertEqual(counts, {r: 20 for r in ROLES})
        for i, cand in enumerate(self.cands):
            self.assertEqual(cand["role_id"], ROLES[i // 20], cand["candidate_id"])

    def test_every_candidate_has_all_fields(self):
        for cand in self.cands:
            for field in CANDIDATE_FIELDS:
                self.assertIn(field, cand, cand["candidate_id"])
            self.assertIn(cand["source"], SOURCES)
            self.assertTrue(cand["name"].strip() and cand["location"].strip())
            self.assertIsInstance(cand["links"], list)
            self.assertEqual(sorted(cand["answers"]), ["q1", "q2", "q3"], cand["candidate_id"])
            for text in cand["answers"].values():
                self.assertTrue(text.strip())

    def test_all_five_sources_and_unique_names(self):
        self.assertEqual({c["source"] for c in self.cands}, SOURCES)
        names = [c["name"] for c in self.cands]
        self.assertEqual(len(set(names)), 60)

    def test_fake_email_phone_and_links(self):
        email_re = re.compile(r"[\w.+'-]+@[\w.-]*\w")
        phone_re = re.compile(r"\b\d{3}-\d{4}\b")
        for cand in self.cands:
            cid = cand["candidate_id"]
            self.assertRegex(cand["email"], r"^[a-z.]+@(example\.com|example\.org|mail\.test)$", cid)
            self.assertRegex(cand["phone"], r"^555-01\d\d$", cid)
            blob = cand["resume_text"] + " " + " ".join(cand["answers"].values())
            for found in email_re.findall(blob):
                self.assertRegex(found, r"@(example\.com|example\.org|[\w.-]+\.test)$", cid)
            for found in phone_re.findall(blob):
                self.assertRegex(found, r"^555-01\d\d$", cid)
            for link in cand["links"]:
                self.assertTrue(link.startswith("https://example.com/"), cid)
            self.assertNotIn("http", blob.replace("https://example.com/", ""), cid)

    def test_resume_word_counts(self):
        for cand in self.cands:
            cid = cand["candidate_id"]
            words = len(cand["resume_text"].split())
            if "thin_resume" in self.key[cid]["traps"]:
                self.assertTrue(40 <= words <= 100, "%s thin resume has %d words" % (cid, words))
            else:
                self.assertTrue(100 <= words <= 320, "%s has %d words" % (cid, words))

    def test_resumes_are_not_templated(self):
        starts = Counter(c["resume_text"].split("\n")[0][:20] for c in self.cands)
        self.assertEqual(max(starts.values()), 1)
        self.assertEqual(len({c["resume_text"] for c in self.cands}), 60)

    # answer key
    def test_answer_key_covers_every_candidate(self):
        self.assertEqual(set(self.key), {c["candidate_id"] for c in self.cands})
        for cand in self.cands:
            entry = self.key[cand["candidate_id"]]
            self.assertEqual(entry["role_id"], cand["role_id"])
            self.assertIn(entry["expected_tier"], TIERS)
            self.assertTrue(set(entry["traps"]) <= TRAPS)
            self.assertGreater(len(entry["why"].split()), 6)
            for tier in entry.get("also_acceptable", []):
                self.assertIn(tier, TIERS)
                self.assertNotEqual(tier, entry["expected_tier"])

    def test_tier_mix(self):
        total = Counter(e["expected_tier"] for e in self.key.values())
        self.assertGreaterEqual(total["strong"], 12)
        self.assertGreaterEqual(total["maybe"], 15)
        self.assertGreaterEqual(total["below"], 15)
        self.assertGreaterEqual(total["review"], 3)
        for role in ROLES:
            per_role = Counter(e["expected_tier"] for e in self.key.values() if e["role_id"] == role)
            self.assertGreaterEqual(per_role["strong"], 4, role)
            self.assertGreaterEqual(per_role["maybe"], 5, role)
            self.assertGreaterEqual(per_role["below"], 5, role)
            self.assertGreaterEqual(per_role["review"], 1, role)

    def test_trap_minimums(self):
        counts = Counter(t for e in self.key.values() for t in e["traps"])
        minimums = {"prompt_injection": 3, "keyword_stuffing": 4, "career_gap": 4, "non_traditional": 4,
                    "non_native_english": 3, "overqualified": 3, "title_inflation": 3, "thin_resume": 2,
                    "long_resume": 2}
        for trap, minimum in minimums.items():
            self.assertGreaterEqual(counts[trap], minimum, trap)

    def test_trap_labels_follow_the_rules(self):
        for cid, entry in self.key.items():
            traps, tier = entry["traps"], entry["expected_tier"]
            if "prompt_injection" in traps:
                self.assertEqual(tier, "review", cid)
            if "non_traditional" in traps or "non_native_english" in traps:
                self.assertEqual(tier, "strong", cid)
            if "career_gap" in traps:
                self.assertNotEqual(tier, "below", cid)
            if "keyword_stuffing" in traps or "title_inflation" in traps:
                self.assertEqual(tier, "below", cid)
            if "overqualified" in traps:
                self.assertEqual(tier, "maybe", cid)

    def test_injection_text_is_really_present(self):
        by_id = {c["candidate_id"]: c["resume_text"].lower() for c in self.cands}
        for cid, entry in self.key.items():
            if "prompt_injection" in entry["traps"]:
                self.assertTrue("ignore" in by_id[cid] or "you are now" in by_id[cid], cid)

    def test_name_pairs_share_a_tier(self):
        pairs = [("C002", "C004"), ("C026", "C029"), ("C049", "C050")]
        for a, b in pairs:
            self.assertEqual(self.key[a]["expected_tier"], self.key[b]["expected_tier"])
            self.assertIn("name_origin_neutral", self.key[a]["traps"])
            self.assertIn("name_origin_neutral", self.key[b]["traps"])

    # hygiene
    def test_no_dashes_or_local_paths_in_sample_folder(self):
        files = [p for p in SAMPLE.iterdir() if p.is_file()]
        self.assertGreaterEqual(len(files), 8)
        for path in files:
            text = path.read_text(encoding="utf-8")
            self.assertNotIn(EM, text, path.name)
            self.assertNotIn(EN, text, path.name)
            self.assertNotIn("/Use" + "rs/", text, path.name)

    def test_expected_files_exist(self):
        for name in ["company.json", "candidates.jsonl", "answer_key.json", "LABELING-GUIDE.md",
                     "application-answers-notes.md"] + ["scorecard-%s.json" % r for r in ROLES]:
            self.assertTrue((SAMPLE / name).is_file(), name)


if __name__ == "__main__":
    unittest.main()
