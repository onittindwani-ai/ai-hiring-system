"""Example 3: screen the made up Bookkeeper candidates with the FAKE Jev, offline.

Usage:
    python3 examples/03_screen_with_mock_jev.py

What it does:
    Starts the practice server (tools/mock_jev.py, a FAKE that guesses from word overlap) on your own
    computer in a background thread, then shows two things:
      1. one raw request: one redacted candidate text and three typed questions, and the typed answers
         that come back (the same shape the real Jev API uses)
      2. the whole screening flow for the 20 Bookkeeper candidates through the same client code the real
         Jev engine uses: blind text in, a level 0 to 4 per criterion out, tiers, then agreement with the
         hand written answer key.
    The fake is NOT the real model. Its numbers say nothing about how well the real Jev scores. To try the
    real one you need your own key (docs/JEV-OPTIONAL.md). Nothing leaves your computer. No key needed.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import evaluate  # noqa: E402
import hlib  # noqa: E402
import jev  # noqa: E402
import mock_jev  # noqa: E402
import score_candidates as sc  # noqa: E402
from redact import redact_text  # noqa: E402

SAMPLE = ROOT / "data" / "sample"
ROLE = "bookkeeper"


def main():
    card, candidates = sc.load_inputs(str(SAMPLE / ("scorecard-%s.json" % ROLE)), str(SAMPLE / "candidates.jsonl"))
    key = hlib.load_json(SAMPLE / "answer_key.json")
    server = mock_jev.start_server()
    try:
        print(mock_jev.BANNER + ". Practice only, never use it to judge people.")
        print("Started on %s (your own computer, nothing leaves it).\n" % mock_jev.server_url(server))
        client = jev.JevClient(api_key="practice-key", base_url=mock_jev.server_url(server), env_file="")

        first = candidates[0]
        blind = redact_text(hlib.candidate_text(first), names=[first.get("name", "")])
        criterion = card["criteria"][0]
        questions = {
            "c_" + criterion["id"]: jev.score(criterion["jev_question"], criterion["levels"]),
            "gate": jev.noul("The text clearly says yes to this question: " + card["gates"][0]["question"]),
        }
        answers, meta = client.ask(blind, questions)
        print("1. ONE REQUEST (candidate %s, name and contact details removed first)" % first["candidate_id"])
        print("   Question: %s" % criterion["jev_question"])
        print("   Answer:   %s" % json.dumps(answers.get("c_" + criterion["id"])))
        print("   Gate:     %s" % json.dumps(answers.get("gate")))
        print("   Input tokens: %s\n" % meta.get("input_tokens"))

        print("2. THE WHOLE FLOW for %d %s candidates" % (len(candidates), ROLE))
        records, tokens = sc.run_scoring(card, candidates, "mock", client=client, unknown_gates_review=False)
        print(sc.summary_text(records))
        print("Input tokens %d, about $%.5f at the starting price estimate.\n" % (tokens, jev.estimate_cost(tokens)))
    finally:
        mock_jev.stop_server(server)

    for record in sc.sort_records(records)[:6]:
        print("  %s  %-6s score %5.1f  %s" % (record["candidate_id"], record["tier"], record["weighted_score"],
                                            "; ".join(record["reasons"][:1])))
    key["candidates"] = {cid: v for cid, v in key["candidates"].items() if v.get("role_id") == ROLE}
    result = evaluate.evaluate(records, key)
    print("\nAgreement with the hand written answer key: %d of %d (%.0f%%)."
          % (result["ok"], result["total"], 100.0 * result["agreement"]))
    print("Dangerous misses (a strong person scored below, or injected wording not sent to review): %d" % len(result["dangerous"]))
    print("This is a fake model. A person decides every no, and every yes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
