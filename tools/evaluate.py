"""Measure a scorer against a hand made answer key (Python 3.9+, standard library only).

Usage:
    python3 tools/evaluate.py --scores scores.json --key data/sample/answer_key.json
    python3 tools/evaluate.py --scores sdr.json bookkeeper.json engineer.json --key data/sample/answer_key.json
    python3 tools/evaluate.py --scores scores.json --key data/sample/answer_key.json --fail-under 0.7

What it does:
    Compares each scored candidate with the tier a hiring manager expected (the answer key) and prints:
      * agreement: how often the tier matches the key (an "also acceptable" tier counts as a match),
      * a confusion table (expected tier down, tool tier across),
      * results per trap (keyword stuffing, career gap, prompt injection, and so on),
      * dangerous misses: a strong person scored below, a person with injected wording not sent to review,
      * candidates in the key that were not scored.
    Use it to see where a scorer is weak BEFORE you trust it on real people. Exit 0 normally; with
    --fail-under, exit 1 when agreement is lower than the number you give.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hlib  # noqa: E402

TIERS = ["strong", "maybe", "review", "below"]


def evaluate(scores, key):
    """Return a dict with the numbers the report prints. `scores` is a list of score records,
    `key` is the loaded answer key."""
    expected = key.get("candidates", {})
    by_id = {r["candidate_id"]: r for r in scores}
    rows, missing = [], []
    for cid, item in sorted(expected.items()):
        record = by_id.get(cid)
        if record is None:
            missing.append(cid)
            continue
        want = item["expected_tier"]
        got = record["tier"]
        ok = got == want or got in item.get("also_acceptable", [])
        rows.append({"id": cid, "expected": want, "got": got, "exact": got == want, "ok": ok,
                     "traps": item.get("traps", []), "why": item.get("why", ""), "score": record.get("weighted_score")})
    confusion = {w: {g: 0 for g in TIERS} for w in TIERS}
    for row in rows:
        if row["expected"] in confusion and row["got"] in confusion[row["expected"]]:
            confusion[row["expected"]][row["got"]] += 1
    traps = {}
    for row in rows:
        for trap in row["traps"]:
            entry = traps.setdefault(trap, {"n": 0, "ok": 0})
            entry["n"] += 1
            entry["ok"] += 1 if row["ok"] else 0
    dangerous = [r for r in rows if (r["expected"] == "strong" and r["got"] == "below")
                 or ("prompt_injection" in r["traps"] and r["got"] != "review")]
    total = len(rows)
    return {"total": total, "exact": sum(r["exact"] for r in rows), "ok": sum(r["ok"] for r in rows),
            "agreement": (sum(r["ok"] for r in rows) / total) if total else 0.0,
            "confusion": confusion, "traps": traps, "dangerous": dangerous, "missing": missing, "rows": rows}


def format_report(result):
    lines = ["Evaluation against the answer key", "",
             "Candidates compared: %d" % result["total"],
             "Same tier as the key: %d (%.0f%%)" % (result["exact"], 100.0 * result["exact"] / max(1, result["total"])),
             "Same or an acceptable tier: %d (%.0f%%)" % (result["ok"], 100.0 * result["agreement"]), "",
             "Confusion (expected down, tool across)", "%-9s" % "" + "".join("%8s" % t for t in TIERS)]
    for want in TIERS:
        lines.append("%-9s" % want + "".join("%8d" % result["confusion"][want][g] for g in TIERS))
    lines += ["", "By trap (matches / candidates)"]
    for trap, entry in sorted(result["traps"].items()):
        lines.append("  %-20s %d / %d" % (trap, entry["ok"], entry["n"]))
    lines += ["", "Dangerous misses: %d" % len(result["dangerous"])]
    for row in result["dangerous"]:
        lines.append("  %s expected %s, tool said %s. %s" % (row["id"], row["expected"], row["got"], row["why"]))
    if result["missing"]:
        lines += ["", "In the key but not scored: " + ", ".join(result["missing"])]
    lines += ["", "A scorer is a helper. A person decides every no."]
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Compare scores with an answer key.")
    parser.add_argument("--scores", required=True, nargs="+", help="one or more scores.json files (one per role is fine)")
    parser.add_argument("--key", required=True)
    parser.add_argument("--fail-under", type=float, help="exit 1 when agreement is below this (0 to 1)")
    args = parser.parse_args(argv)
    try:
        scores = [row for path in args.scores for row in hlib.load_json(path)]
        key = hlib.load_json(args.key)
        result = evaluate(scores, key)
    except (OSError, ValueError, KeyError) as err:
        print("Could not read the inputs: %s" % err)
        return 1
    if not result["total"]:
        print("No scored candidate matches the answer key. Check the ids and the role.")
        return 1
    print(format_report(result))
    if args.fail_under is not None and result["agreement"] < args.fail_under:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
