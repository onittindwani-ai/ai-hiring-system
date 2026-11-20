"""Smoke test for Jev: one small request, prints the answers and the cost (Python 3.9+, standard library only).

Usage:
    python3 tools/jev_check.py            # real Jev, needs TYPESAFE_API_KEY (docs/JEV-OPTIONAL.md)
    python3 tools/jev_check.py --mock     # the FAKE practice server, no key, no cost

What it does:
    Sends one short example text with three questions (a choice, a score, a yes or no) and prints what came
    back. Run it once after setup to prove your key works. Exit 0 if it worked, 1 if not.
    Never put a key in the AI chat: set it in your own terminal or in a local .env file.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import jev  # noqa: E402
import mock_jev  # noqa: E402

STATE = ("I led a support desk of four people. I answered about 40 tickets a day, wrote the help articles "
         "for our top 10 questions, and trained two new hires in the first month.")

QUESTIONS = {
    "level": jev.choice("Which level of job does this person describe", {
        "entry": "First or second job, mostly learning",
        "mid": "Solid experience, works alone",
        "lead": "Leads people or owns a process"}),
    "ownership": jev.score("How strongly the text shows the person owned the work", [
        "No evidence", "Mentioned only", "Did it with help", "Did it on their own", "Did it and taught others"]),
    "trains_others": jev.noul("The person trained or taught other people"),
}


def run(client):
    answers, meta = client.ask(STATE, QUESTIONS)
    print("Jev answered in %.2f seconds (model %s)" % (meta["seconds"], meta["model"]))
    option, prob, conf = jev.top_choice(answers["level"])
    print("  level        : %s (probability %.2f, confidence %.2f)" % (option, prob, conf))
    print("  ownership    : %s of 4 (confidence %s)" % (answers["ownership"].get("score"),
                                                         answers["ownership"].get("confidence")))
    print("  trains_others: %s (0 = no, 1 = yes)" % answers["trains_others"].get("noul"))
    cost = jev.estimate_cost(meta["input_tokens"])
    print("  tokens in/out: %s/%s, estimated cost about $%.6f (starting estimate, check typesafe.ai)"
          % (meta["input_tokens"], meta["output_tokens"], cost))


def main(argv=None):
    parser = argparse.ArgumentParser(description="One small Jev request to prove setup works.")
    parser.add_argument("--mock", action="store_true", help="use the FAKE practice server (no key, no cost)")
    args = parser.parse_args(argv)
    server = None
    try:
        if args.mock:
            print(mock_jev.BANNER + ".")
            server = mock_jev.start_server()
            client = jev.JevClient(api_key="practice-key", base_url=mock_jev.server_url(server))
        else:
            client = jev.JevClient()
        run(client)
    except jev.JevError as err:
        print("FAILED: %s" % err)
        return 1
    finally:
        if server is not None:
            mock_jev.stop_server(server)
    print("OK: Jev setup works." if not args.mock else "OK: the fake server works. Real Jev: docs/JEV-OPTIONAL.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
